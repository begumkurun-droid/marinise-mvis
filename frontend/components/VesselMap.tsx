"use client";

import { useEffect, useRef, useState } from "react";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import { useRouter } from "next/navigation";
import { getLiveMap, VesselListItem } from "@/lib/api";

// Section 3: "Harita üzerinde gemilerin tiplerine göre farklı renk ve ikonlar
// kullanılmalıdır." One color per vessel type.
const TYPE_COLORS: Record<string, string> = {
  superyacht: "#F4792E",
  motor_yacht: "#F4792E",
  sailing_yacht: "#E0A458",
  commercial_vessel: "#0B2545",
  container_vessel: "#2C6E9B",
  bulk_carrier: "#6C584C",
  tanker: "#8E2E2E",
  tugboat: "#4C6B5A",
  offshore_vessel: "#5A3E85",
  passenger_vessel: "#2E8E7C",
  cruise_ship: "#2E8E7C",
  fishing_vessel: "#B08D57",
  service_vessel: "#777777",
  other: "#999999",
};

// Free, no-API-key vector basemap (per FAZ 0 architecture research: MapLibre
// needs a vector-tile source; OpenFreeMap is the zero-cost option).
const MAP_STYLE = "https://tiles.openfreemap.org/styles/liberty";

export default function VesselMap() {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);
  const markersRef = useRef<maplibregl.Marker[]>([]);
  const router = useRouter();
  const [vesselCount, setVesselCount] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;

    mapRef.current = new maplibregl.Map({
      container: containerRef.current,
      style: MAP_STYLE,
      center: [29.5, 39.5], // Türkiye kıyıları merkezli (Section 4 öncelikli bölgeler)
      zoom: 5.2,
    });
    mapRef.current.addControl(new maplibregl.NavigationControl(), "top-right");

    return () => {
      mapRef.current?.remove();
      mapRef.current = null;
    };
  }, []);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const vessels = await getLiveMap();
        if (cancelled || !mapRef.current) return;

        markersRef.current.forEach((m) => m.remove());
        markersRef.current = [];

        vessels.forEach((v: VesselListItem) => {
          if (!v.last_position) return;
          const color = TYPE_COLORS[v.vessel_type] ?? TYPE_COLORS.other;

          const el = document.createElement("div");
          el.style.width = "14px";
          el.style.height = "14px";
          el.style.borderRadius = "50%";
          el.style.background = color;
          el.style.border = "2px solid white";
          el.style.boxShadow = "0 0 2px rgba(0,0,0,0.5)";
          el.style.cursor = "pointer";

          const popup = new maplibregl.Popup({ offset: 12 }).setHTML(
            `<strong>${v.name}</strong><br/>${v.vessel_type}<br/>${
              v.last_position?.speed_over_ground_kn ?? "-"
            } kn`
          );

          const marker = new maplibregl.Marker({ element: el })
            .setLngLat([v.last_position.longitude, v.last_position.latitude])
            .setPopup(popup)
            .addTo(mapRef.current!);

          el.addEventListener("click", () => router.push(`/vessels/${v.id}`));
          markersRef.current.push(marker);
        });

        setVesselCount(vessels.length);
      } catch {
        if (!cancelled) setError("Canlı gemi verisi alınamadı. Backend/AIS worker çalışıyor mu?");
      }
    }

    load();
    const interval = setInterval(load, 15000); // Section 3: near-real-time refresh
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, [router]);

  return (
    <div className="relative h-full w-full">
      <div ref={containerRef} className="h-full w-full" />
      <div className="absolute left-3 top-3 rounded bg-white/95 px-3 py-1.5 text-xs shadow">
        {error ? (
          <span className="text-red-600">{error}</span>
        ) : (
          <span>
            Takip edilen gemi: <strong>{vesselCount ?? "…"}</strong>
          </span>
        )}
      </div>
    </div>
  );
}
