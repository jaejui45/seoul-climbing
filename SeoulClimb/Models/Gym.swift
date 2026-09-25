import Foundation
import CoreLocation

struct GymData: Decodable {
    let updated: String
    let gyms: [Gym]
}

struct Gym: Identifiable, Decodable, Hashable {
    enum Category: String, Decodable {
        case indoor = "실내 클라이밍장"
        case outdoor = "야외 인공암벽"
    }

    let id: Int
    let name: String
    let category: Category
    let district: String
    let address: String
    let latitude: Double
    let longitude: Double
    let phone: String?
    /// 월~일 7개. nil = 영업시간 정보 없음, 원소 nil = 휴무, [open, close] = "HH:mm" (close는 최대 "24:00")
    let hours: [[String]?]?
    /// 공휴일 영업시간. nil 이면 등록된 정보가 없다.
    let holidayHours: [String]?
    /// 업체 홈페이지 또는 인스타그램
    let link: String?
    /// 카카오맵 장소 ID
    let kakaoId: String?
    let source: String
    /// 출처에서 정보가 마지막으로 갱신된 날짜
    let checked: String?

    var kakaoURL: URL? {
        kakaoId.flatMap { URL(string: "https://place.map.kakao.com/\($0)") }
    }
    var linkURL: URL? {
        link.flatMap { URL(string: $0) }
    }

    var coordinate: CLLocationCoordinate2D {
        CLLocationCoordinate2D(latitude: latitude, longitude: longitude)
    }
}

// MARK: - 영업시간 계산

enum OpenStatus: Equatable {
    case open(closesAt: String)
    case opensLater(opensAt: String)
    case closedToday
    case unknown

    var isOpen: Bool {
        if case .open = self { return true }
        return false
    }
}

extension Gym {
    static let seoulCalendar: Calendar = {
        var cal = Calendar(identifier: .gregorian)
        cal.timeZone = TimeZone(identifier: "Asia/Seoul")!
        return cal
    }()

    static let weekdayNames = ["월", "화", "수", "목", "금", "토", "일"]

    /// 월=0 … 일=6
    static func weekdayIndex(for date: Date) -> Int {
        let wd = seoulCalendar.component(.weekday, from: date) // 일=1 … 토=7
        return (wd + 5) % 7
    }

    static func minutes(_ hhmm: String) -> Int {
        let p = hhmm.split(separator: ":").compactMap { Int($0) }
        guard p.count == 2 else { return 0 }
        return p[0] * 60 + p[1]
    }

    func hours(onDayIndex i: Int) -> [String]? {
        guard let hours, hours.indices.contains(i) else { return nil }
        return hours[i]
    }

    var is24Hours: Bool {
        hours?.allSatisfy { $0 == ["00:00", "24:00"] } ?? false
    }

    func hoursText(dayIndex i: Int) -> String {
        guard hours != nil else { return "정보 없음" }
        guard let h = hours(onDayIndex: i) else { return "휴무" }
        if h == ["00:00", "24:00"] { return "24시간" }
        return "\(h[0]) – \(h[1])"
    }

    func status(at date: Date = .now) -> OpenStatus {
        guard hours != nil else { return .unknown }
        let cal = Self.seoulCalendar
        let now = cal.component(.hour, from: date) * 60 + cal.component(.minute, from: date)
        let today = Self.weekdayIndex(for: date)

        // 전날 영업이 자정을 넘기는 경우 (예: 18:00–26:00)
        let yesterday = (today + 6) % 7
        if let y = hours(onDayIndex: yesterday), Self.minutes(y[1]) > 24 * 60,
           now < Self.minutes(y[1]) - 24 * 60 {
            return .open(closesAt: y[1])
        }

        guard let h = hours(onDayIndex: today) else { return .closedToday }
        let open = Self.minutes(h[0]), close = Self.minutes(h[1])
        if now >= open && now < close { return .open(closesAt: h[1] == "24:00" ? "자정" : h[1]) }
        if now < open { return .opensLater(opensAt: h[0]) }
        return .closedToday
    }
}
