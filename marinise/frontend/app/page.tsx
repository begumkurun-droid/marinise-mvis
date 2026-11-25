"use client";

import { useEffect, useState } from "react";
import { DashboardSummary, getDashboardSummary } from "@/lib/api";

function StatCard({ label, value, accent }: { label: string; value: string | number; accent?: boolean }) {
  return (
    <div className={`rounded-lg border p-4 shadow-sm ${accent ? "border-marinise-orange bg-marinise-orange/5" : "border-gray-200 bg-white"}`}>
      <p className="text-xs uppercase tracking-wide text-gray-500">{label}</p>
      <p className="mt-1 text-2xl font-bold text-marinise-navy">{value}</p>
    </div>
  );
}

export default function DashboardPage() {
  const [data, setData] = useState<DashboardSummary | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getDashboardSummary()
      .then(setData)
      .catch(() => setError("Dashboard verisi alınamadı. Giriş yaptınız mı?"));
  }, []);

  return (
    <div className="p-6">
      <h1 className="mb-1 text-xl font-bold text-marinise-navy">Executive Dashboard</h1>
      <p className="mb-6 text-sm text-gray-500">
        Section 14 gereği tüm rakamlar canlı veri tabanından okunur; sahte istatistik gösterilmez.
      </p>

      {error && <p className="text-sm text-red-600">{error}</p>}

      {data && (
        <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
          <StatCard label="Aktif Takip Edilen Gemi" value={data.active_tracked_vessels} />
          <StatCard label="Türkiye'deki Gemi" value={data.vessels_in_turkey} />
          <StatCard label="Türkiye'ye Yaklaşan" value={data.vessels_approaching_turkey} />
          <StatCard label="CAT Motorlu Gemi" value={data.cat_engine_vessels} accent />
          <StatCard label="MASE Jeneratörlü Yat" value={data.mase_generator_vessels} accent />
          <StatCard label="Yeni Lead (7 gün)" value={data.new_leads_last_7_days} />
          <StatCard label="High Priority Lead" value={data.high_priority_leads} accent />
          <StatCard label="Veri Doğrulama Oranı" value={`%${data.data_verification_rate_pct}`} />
          <StatCard label="İletişim Bilgisi Bulunma Oranı" value={`%${data.contact_info_found_rate_pct}`} />
        </div>
      )}
    </div>
  );
}
