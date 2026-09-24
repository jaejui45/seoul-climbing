import Foundation
import CoreLocation
import Observation

@Observable
final class GymStore {
    enum Filter: String, CaseIterable, Identifiable {
        case all = "전체"
        case openNow = "지금 영업중"
        case indoor = "실내"
        case outdoor = "야외"
        var id: String { rawValue }
    }

    private(set) var gyms: [Gym] = []
    private(set) var updated = ""
    var searchText = ""
    var filter: Filter = .all

    init() { load() }

    private func load() {
        guard let url = Bundle.main.url(forResource: "gyms", withExtension: "json"),
              let data = try? Data(contentsOf: url),
              let decoded = try? JSONDecoder().decode(GymData.self, from: data) else {
            assertionFailure("gyms.json 로드 실패")
            return
        }
        gyms = decoded.gyms
        updated = decoded.updated
    }

    func filtered(now: Date = .now, near location: CLLocation?) -> [Gym] {
        let q = searchText.trimmingCharacters(in: .whitespaces)
        let list = gyms.filter { gym in
            switch filter {
            case .all: break
            case .openNow: guard gym.status(at: now).isOpen else { return false }
            case .indoor: guard gym.category == .indoor else { return false }
            case .outdoor: guard gym.category == .outdoor else { return false }
            }
            guard !q.isEmpty else { return true }
            return gym.name.localizedCaseInsensitiveContains(q)
                || gym.district.contains(q)
                || gym.address.contains(q)
        }
        guard let location else { return list }
        return list.sorted { distance(to: $0, from: location) < distance(to: $1, from: location) }
    }

    func distance(to gym: Gym, from location: CLLocation) -> CLLocationDistance {
        location.distance(from: CLLocation(latitude: gym.latitude, longitude: gym.longitude))
    }
}
