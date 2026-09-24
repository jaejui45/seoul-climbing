import SwiftUI
import MapKit

struct GymMapView: View {
    @Environment(GymStore.self) private var store
    @Environment(LocationManager.self) private var location

    @State private var camera: MapCameraPosition = .region(
        MKCoordinateRegion(center: CLLocationCoordinate2D(latitude: 37.5400, longitude: 126.9900),
                           span: MKCoordinateSpan(latitudeDelta: 0.22, longitudeDelta: 0.22))
    )
    @State private var selected: Gym?

    var body: some View {
        @Bindable var store = store
        NavigationStack {
            TimelineView(.everyMinute) { context in
                let gyms = store.filtered(now: context.date, near: nil)
                Map(position: $camera, selection: $selected) {
                    UserAnnotation()
                    ForEach(gyms) { gym in
                        Marker(gym.name,
                               systemImage: gym.category == .indoor ? "figure.climbing" : "mountain.2.fill",
                               coordinate: gym.coordinate)
                            .tint(Self.color(for: gym.status(at: context.date)))
                            .tag(gym)
                    }
                }
                .mapControls {
                    MapUserLocationButton()
                    MapCompass()
                    MapScaleView()
                }
            }
            .safeAreaInset(edge: .top) {
                FilterBar(filter: $store.filter)
                    .padding(.vertical, 6)
                    .background(.bar)
            }
            .navigationTitle("서울 클라이밍장")
            .navigationBarTitleDisplayMode(.inline)
            .sheet(item: $selected) { gym in
                NavigationStack { GymDetailView(gym: gym) }
                    .presentationDetents([.medium, .large])
            }
        }
    }

    static func color(for status: OpenStatus) -> Color {
        switch status {
        case .open: .green
        case .opensLater: .orange
        case .closedToday: .red
        case .unknown: .gray
        }
    }
}
