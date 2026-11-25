"use client";

import { useCallback, useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { VesselDetail, getVessel } from "@/lib/api";
import CompanyResearchPanel from "@/components/CompanyResearchPanel";

const VERIFICATION_LABEL: Record<string, string> = {
  verified: "Doğrulandı",
  partially_verified: "Kısmen doğrulandı",
  unverified: "Doğrulanmadı",
  conflicting_information: "Çelişkili bilgi",
  unknown: "Bilinmiyor",
};

export default function VesselDetailPage() {
  const params = useParams();
  const id = Number(params.id);
  const [vessel, setVessel] = useState<VesselDetail | null>(null);
  const [error, setError] = useState<string | null>(null);

  const reload = useCallback(() => {
    getVessel(id)
      .then(setVessel)
      .catch(() => setError("Gemi bulunamadı ya da erişim yetkiniz yok."));
  }, [id]);

  useEffect(() => {
    reload();
  }, [reload]);

  if (error) return <p className="p-6 text-sm text-red-600">{error}</p>;
  if (!vessel) return <p className="p-6 text-sm text-gray-400">Yükleniyor…</p>;

  return (
    <div className="p-6">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-marinise-navy">{vessel.name}</h1>
          <p className="text-sm text-gray-500">
            {vessel.vessel_type} · {vessel.flag ?? "Bayrak bilinmiyor"} · IMO {vessel.imo_number ?? "-"} · MMSI{" "}
            {vessel.mmsi ?? "-"}
          </p>
        </div>
        {vessel.lead_score !== null && (
          <div className="rounded-lg bg-marinise-orange/10 px-4 py-2 text-center">
            <p className="text-xs text-gray-500">Lead Score</p>
            <p className="text-lg font-bold text-marinise-orange">{vessel.lead_score}</p>
            <p className="text-xs uppercase text-gray-500">{vessel.lead_priority}</p>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <section className="rounded-lg bg-white p-4 shadow-sm">
          <h2 className="mb-3 font-semibold text-marinise-navy">Engine Intelligence</h2>
          {vessel.engines.length === 0 && (
            <p className="text-sm text-gray-400">Henüz makine verisi kaydedilmedi.</p>
          )}
          <table className="w-full text-sm">
            <tbody>
              {vessel.engines.map((e, i) => (
                <tr key={i} className="border-b border-gray-100">
                  <td className="py-1.5 pr-2 text-gray-500">{e.category}</td>
                  <td className="py-1.5 pr-2 font-medium">
                    {e.manufacturer_name ?? "-"} {e.engine_model_raw ?? ""}
                  </td>
                  <td className="py-1.5 pr-2">×{e.quantity}</td>
                  <td className="py-1.5">
                    <span className="rounded bg-gray-100 px-2 py-0.5 text-xs">
                      {VERIFICATION_LABEL[e.verification_status] ?? e.verification_status} ({e.confidence_score})
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>

        <CompanyResearchPanel vesselId={vessel.id} companies={vessel.companies} onSaved={reload} />

        <section className="rounded-lg bg-white p-4 shadow-sm md:col-span-2">
          <h2 className="mb-3 font-semibold text-marinise-navy">Son Konum</h2>
          {vessel.last_position ? (
            <p className="text-sm text-gray-700">
              {vessel.last_position.latitude.toFixed(4)}, {vessel.last_position.longitude.toFixed(4)} ·{" "}
              {vessel.last_position.speed_over_ground_kn ?? "-"} kn ·{" "}
              {new Date(vessel.last_position.received_at).toLocaleString("tr-TR")}
            </p>
          ) : (
            <p className="text-sm text-gray-400">Henüz AIS konumu alınmadı.</p>
          )}
        </section>
      </div>
    </div>
  );
}
