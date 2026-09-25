import SwiftUI
import MapKit

struct GymDetailView: View {
    let gym: Gym
    @Environment(\.openURL) private var openURL

    var body: some View {
        TimelineView(.everyMinute) { context in
            let today = Gym.weekdayIndex(for: context.date)
            List {
                Section {
                    VStack(alignment: .leading, spacing: 8) {
                        Text(gym.category.rawValue)
                            .font(.caption)
                            .foregroundStyle(.secondary)
                        OpenStatusBadge(status: gym.status(at: context.date))
                    }
                    Map(initialPosition: .region(MKCoordinateRegion(center: gym.coordinate,
                                                                    latitudinalMeters: 600, longitudinalMeters: 600))) {
                        Marker(gym.name, systemImage: "figure.climbing", coordinate: gym.coordinate)
                            .tint(.orange)
                    }
                    .frame(height: 180)
                    .clipShape(RoundedRectangle(cornerRadius: 10))
                    .allowsHitTesting(false)
                    .listRowInsets(EdgeInsets(top: 8, leading: 16, bottom: 8, trailing: 16))
                }

                Section("영업시간") {
                    if gym.hours == nil {
                        Text("등록된 영업시간 정보가 없습니다. 아래 카카오맵에서 확인해 주세요.")
                            .foregroundStyle(.secondary)
                    } else {
                        ForEach(0..<7, id: \.self) { i in
                            HStack {
                                Text(Gym.weekdayNames[i] + "요일")
                                    .fontWeight(i == today ? .bold : .regular)
                                Spacer()
                                Text(gym.hoursText(dayIndex: i))
                                    .monospacedDigit()
                                    .fontWeight(i == today ? .bold : .regular)
                                    .foregroundStyle(gym.hours(onDayIndex: i) == nil ? .red : .primary)
                            }
                            .listRowBackground(i == today ? Color.orange.opacity(0.12) : nil)
                        }
                        if let holiday = gym.holidayHours {
                            HStack {
                                Text("공휴일")
                                Spacer()
                                Text("\(holiday[0]) – \(holiday[1])")
                                    .monospacedDigit()
                            }
                            .foregroundStyle(.secondary)
                        }
                    }
                }

                Section("위치") {
                    LabeledContent("구", value: gym.district)
                    Text(gym.address)
                        .textSelection(.enabled)
                    Button {
                        openAppleMaps()
                    } label: {
                        Label("Apple 지도로 길찾기", systemImage: "arrow.triangle.turn.up.right.diamond")
                    }
                    if let url = gym.kakaoURL {
                        Button { openURL(url) } label: {
                            Label("카카오맵에서 보기", systemImage: "map")
                        }
                    }
                    Button {
                        openNaverMap()
                    } label: {
                        Label("네이버 지도에서 보기", systemImage: "map.fill")
                    }
                    if let url = gym.linkURL {
                        Button { openURL(url) } label: {
                            Label(url.host?.contains("instagram") == true ? "인스타그램" : "홈페이지",
                                  systemImage: "link")
                        }
                    }
                    if let phone = gym.phone, let url = URL(string: "tel:" + phone.filter(\.isNumber)) {
                        Button {
                            openURL(url)
                        } label: {
                            Label(phone, systemImage: "phone")
                        }
                    }
                }

                Section {
                    Text(gym.checked.map { "출처: \(gym.source) · \($0) 갱신" } ?? "출처: \(gym.source)")
                    Text("공휴일·이벤트·세팅일에는 영업시간이 달라질 수 있어요.")
                }
                .font(.footnote)
                .foregroundStyle(.secondary)
            }
        }
        .navigationTitle(gym.name)
        .navigationBarTitleDisplayMode(.inline)
    }

    private func openAppleMaps() {
        var c = URLComponents(string: "https://maps.apple.com/")!
        c.queryItems = [
            URLQueryItem(name: "daddr", value: "\(gym.latitude),\(gym.longitude)"),
            URLQueryItem(name: "q", value: gym.name),
            URLQueryItem(name: "dirflg", value: "r"),
        ]
        if let url = c.url { openURL(url) }
    }

    private func openNaverMap() {
        let query = gym.name.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? ""
        let app = URL(string: "nmap://search?query=\(query)&appname=com.jaehyeong.SeoulClimb")!
        let web = URL(string: "https://map.naver.com/p/search/\(query)")!
        openURL(app) { accepted in
            if !accepted { openURL(web) }
        }
    }
}
