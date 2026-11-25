"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ResearchQueueItem, getResearchQueue } from "@/lib/api";

export default function OwnershipResearchQueuePage() {
  const [items, setItems] = useState<ResearchQueueItem[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getResearchQueue()
      .then(setItems)
      .catch(() => setError("Liste alınamadı."));
  }, []);

  return (
    <div className="p-6">
      <h1 className="mb-1 text-xl font-bold text-marinise-navy">Ownership & Management — Araştırma Kuyruğu</h1>
      <p className="mb-4 text-sm text-gray-500">
        Henüz owner/management şirketi kaydedilmemiş gemiler (Section 7/8). Bir gemiye tıklayıp
        Equasis/IMO GISIS üzerinden elle araştırma yapıp sonucu kaydedebilirsiniz.
      </p>

      {error && <p className="text-sm text-red-600">{error}</p>}

      <ul className="divide-y divide-gray-100 rounded-lg bg-white shadow-sm">
        {items.map((v) => (
          <li key={v.id} className="flex items-center justify-between px-4 py-3 text-sm">
            <div>
              <Link href={`/vessels/${v.id}`} className="font-medium text-marinise-navy hover:underline">
                {v.name}
              </Link>
              <span className="ml-2 text-gray-400">
                {v.vessel_type} · IMO {v.imo_number ?? "-"} · MMSI {v.mmsi ?? "-"}
              </span>
            </div>
            <span className="rounded bg-gray-100 px-2 py-0.5 text-xs">{v.customer_status}</span>
          </li>
        ))}
        {items.length === 0 && (
          <li className="px-4 py-6 text-center text-gray-400">
            Tüm gemilerin owner/management bilgisi kaydedilmiş. 🎉
          </li>
        )}
      </ul>
    </div>
  );
}
