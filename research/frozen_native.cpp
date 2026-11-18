// Exact implementation of the frozen greedy and conflict-loss ordering for grouped candidate streams.
#include <algorithm>
#include <cstdint>
#include <cstring>
#include <map>
#include <numeric>
#include <tuple>
#include <unordered_map>
#include <unordered_set>
#include <vector>

struct Row {
    int32_t target, site, start, end, points, window;
    char id[16];
};
struct Slot { int32_t target, site, start, end; };
using Check = int (*)();
static_assert(sizeof(Row) == 40 && sizeof(Slot) == 16, "Python ABI");
struct Occupancy {
    struct Timeline { std::vector<Slot> rows; int max_duration = 0; };
    std::unordered_map<int,Timeline> sites;
    void insert(Slot s) {
        auto &time = sites[s.site];
        auto pos = std::lower_bound(time.rows.begin(), time.rows.end(), s.start,
            [](const Slot &r, int a) { return r.start < a; });
        time.rows.insert(pos, s);
        time.max_duration = std::max(time.max_duration, s.end - s.start);
    }
    bool free(const Row &r) const {
        auto p = sites.find(r.site);
        if (p == sites.end()) return true;
        const auto &time = p->second;
        auto pos = std::lower_bound(time.rows.begin(), time.rows.end(), r.start - time.max_duration - 29,
            [](const Slot &s, int a) { return s.start < a; });
        for (; pos != time.rows.end() && pos->start < r.end + 30; ++pos) {
            const int gap = r.target == pos->target ? 0 : 30;
            if (pos->start < r.end + gap && pos->end + gap > r.start) return false;
        }
        return true;
    }
    void accept(const Row &r) { insert({r.target,r.site,r.start,r.end}); }
};

struct Group {
    int target = 0, max_points = 0;
    std::vector<int> candidates;
    std::unordered_set<int> windows;
};
struct Interval { int group, lo, past; double contribution; };
struct Change { int at, points, delta; };
constexpr int bin_width = 128;
using Bins = std::vector<std::vector<Interval>>;
using LossIndex = std::map<std::pair<int,int>, Bins>;

// For a trial starting at s, another candidate overlaps iff
// other.start - trial.duration - 30 < s < other.end + 30 (strict, integer seconds).
// Sweep each other target separately. Its intervals are disjoint and carry the same
// maximum score as the original affected[target] dictionary. Append groups in source
// order so binary64 additions follow Python 3.11 dictionary insertion order.
static LossIndex build_index(const Row *rows, const std::vector<Group> &groups,
                            const std::unordered_set<int> &durations, int horizon, Check check, bool &expired) {
    LossIndex index;
    for (int g = 0; g < (int)groups.size(); ++g) {
        if (check()) { expired = true; return {}; }
        const auto &group = groups[g];
        std::map<int,std::vector<int>> by_site;
        for (int i : group.candidates) by_site[rows[i].site].push_back(i);
        for (const auto &[site, ids] : by_site) for (int duration : durations) {
            auto &bins = index[{site,duration}];
            if (bins.empty()) bins.resize(horizon/bin_width + 1);
            std::vector<Change> events;
            events.reserve(ids.size()*2);
            for (int i : ids) {
                const Row &r = rows[i];
                events.push_back({std::max(0,r.start-duration-29),r.points,1});
                events.push_back({std::min(horizon+1,r.end+30),r.points,-1});
            }
            std::sort(events.begin(),events.end(),[](const Change &a,const Change &b) { return a.at<b.at; });
            std::map<int,int> active;
            int last = events.front().at;
            std::vector<Interval> ranges;
            for (size_t i=0; i<events.size();) {
                const int at=events[i].at;
                if (last<at && !active.empty()) {
                    const double contribution = static_cast<double>(active.rbegin()->first)/group.candidates.size();
                    if (!ranges.empty() && ranges.back().past==last && ranges.back().contribution==contribution)
                        ranges.back().past=at;
                    else ranges.push_back({g,last,at,contribution});
                }
                while (i<events.size() && events[i].at==at) {
                    const auto &e=events[i++];
                    auto &v=active[e.points];
                    v+=e.delta;
                    if (v==0) active.erase(e.points);
                }
                last=at;
            }
            for (const auto &span:ranges)
                for (int b=span.lo/bin_width;b<=(span.past-1)/bin_width;++b) bins[b].push_back(span);
        }
    }
    return index;
}

extern "C" __declspec(dllexport) int select_rows(const Row *rows, int count, const Slot *fixed,
        int nfixed, const Slot *fragments, int nfragments, int method, int32_t *answer, Check check) {
    try {
        Occupancy occupancy;
        std::unordered_set<int> fixed_targets;
        for (int i=0;i<nfixed;++i) {
            occupancy.insert(fixed[i]);
            fixed_targets.insert(fixed[i].target);
        }
        for (int i=0;i<nfragments;++i) occupancy.insert(fragments[i]);
        int selected=0;
        if (method==0) {
            std::vector<int> order(count);
            std::iota(order.begin(),order.end(),0);
            std::stable_sort(order.begin(),order.end(),[&](int i,int j) {
                const auto &a=rows[i], &b=rows[j];
                const auto ka=std::make_tuple(a.start,a.start-a.end,a.site,a.target);
                const auto kb=std::make_tuple(b.start,b.start-b.end,b.site,b.target);
                return ka!=kb ? ka<kb : std::strcmp(a.id,b.id)<0;
            });
            int visited=0;
            for (int i : order) {
                if ((visited++ % 2048)==0 && check()) return -3;
                const auto &r = rows[i];
                if (!fixed_targets.count(r.target) && occupancy.free(r)) {
                    fixed_targets.insert(r.target); occupancy.accept(r); answer[selected++]=i;
                }
            }
            return selected;
        }
        std::vector<Group> groups;
        std::unordered_map<int,int> group_index;
        std::unordered_set<int> durations;
        int horizon=0;
        for (int i=0;i<count;++i) {
            const auto &r=rows[i];
            if (fixed_targets.count(r.target)) continue;
            auto [p,added]=group_index.emplace(r.target,(int)groups.size());
            if (added) { groups.emplace_back(); groups.back().target=r.target; }
            if (p->second!=(int)groups.size()-1 || r.start<0 || r.end<=r.start || r.points<=0) return -2;
            auto &group=groups[p->second];
            group.candidates.push_back(i);
            group.windows.insert(r.window); group.max_points=std::max(group.max_points,r.points);
            durations.insert(r.end-r.start); horizon=std::max(horizon,r.end);
        }
        std::vector<int> order(groups.size());
        std::iota(order.begin(),order.end(),0);
        auto order_key=[&](int i) {
            const auto &g=groups[i];
            return std::make_tuple(-g.max_points,g.windows.size(),g.candidates.size(),g.target);
        };
        std::sort(order.begin(),order.end(),[&](int i,int j){ return order_key(i)<order_key(j); });
        bool expired=false;
        const auto index=build_index(rows,groups,durations,horizon,check,expired);
        if (expired) return -3;
        std::vector<bool> consumed(groups.size(),false);
        for (int g : order) {
            if (check()) return -3;
            consumed[g]=true;
            std::vector<int> best_points_rows;
            int best_points=-1;
            for (int i : groups[g].candidates) {
                const auto &r=rows[i];
                if (r.points<best_points || !occupancy.free(r)) continue;
                if (r.points>best_points) { best_points=r.points; best_points_rows.clear(); }
                best_points_rows.push_back(i);
            }
            int best=-1;
            std::tuple<double,int,int,int> best_key;
            for (int i : best_points_rows) {
                const auto &r=rows[i];
                double loss=0; int affected=0;
                const auto &bin=index.at({r.site,r.end-r.start})[r.start/bin_width];
                for (const auto &span:bin) {
                    if (!consumed[span.group] && span.lo<=r.start && r.start<span.past) {
                        loss+=span.contribution; ++affected;
                    }
                }
                auto key=std::make_tuple(loss,affected,r.start,r.site);
                if (best<0 || key<best_key || (key==best_key && std::strcmp(r.id,rows[best].id)<0)) {
                    best=i; best_key=key;
                }
            }
            if (best>=0) { occupancy.accept(rows[best]); answer[selected++]=best; }
        }
        return selected;
    } catch (...) { return -4; }
}

