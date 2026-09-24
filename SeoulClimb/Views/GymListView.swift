import SwiftUI
import CoreLocation

struct GymListView: View {
    @Environment(GymStore.self) private var store
    @Environment(LocationManager.self) private var location

    var body: some View {
        @Bindable var store = store
        NavigationStack {
            TimelineView(.everyMinute) { context in
                let gyms = store.filtered(now: context.date, near: location.location)
                List {
                    Section {
                        ForEach(gyms) { gym in
                            NavigationLink(value: gym) {
                                GymRow(gym: gym, now: context.date, distance: location.location.map { store.distance(to: gym, from: $0) })
                            }
                        }
                    } header: {
                        Text(location.location == nil ? "\(gyms.count)곳" : "\(gyms.count)곳 · 가까운 순")
                    } footer: {
                        Text("영업시간 기준일 \(store.updated). 공휴일·이벤트로 달라질 수 있으니 방문 전 확인하세요.")
                    }
                }
                .listStyle(.insetGrouped)
                .overlay {
                    if gyms.isEmpty {
                        ContentUnavailableView.search(text: store.searchText)
                    }
                }
            }
            .safeAreaInset(edge: .top) {
                FilterBar(filter: $store.filter)
                    .padding(.vertical, 6)
                    .background(.bar)
            }
            .navigationTitle("서울 클라이밍장")
            .navigationBarTitleDisplayMode(.inline)
            .searchable(text: $store.searchText, prompt: "이름, 구, 주소 검색")
            .navigationDestination(for: Gym.self) { GymDetailView(gym: $0) }
        }
    }
}

struct GymRow: View {
    let gym: Gym
    let now: Date
    let distance: CLLocationDistance?

    var body: some View {
        VStack(alignment: .leading, spacing: 5) {
            HStack {
                Text(gym.name).font(.headline)
                Spacer()
                if let distance {
                    Text(Self.format(distance))
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
            }
            HStack(spacing: 6) {
                Text(gym.district)
                Text("·")
                Text(gym.category == .indoor ? "실내" : "야외 인공암벽")
                Text("·")
                Text("오늘 \(gym.hoursText(dayIndex: Gym.weekdayIndex(for: now)))")
            }
            .font(.caption)
            .foregroundStyle(.secondary)
            OpenStatusBadge(status: gym.status(at: now))
        }
        .padding(.vertical, 2)
    }

    static func format(_ meters: CLLocationDistance) -> String {
        meters < 1000 ? "\(Int(meters))m" : String(format: "%.1fkm", meters / 1000)
    }
}
