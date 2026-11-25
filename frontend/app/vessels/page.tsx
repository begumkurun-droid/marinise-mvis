"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { VesselListItem, listVessels } from "@/lib/api";

export default function VesselDatabasePage() {
  const [name, setName] = useState("");
  const [engineManufacturer, setEngineManufacturer] = useState("");
  const [vessels, setVessels] = useState<VesselListItem[]>([]);
  const [error, setError] = useState<string | null>(null);

  async function runSearch() {
    const params = new URLSearchParams();
    if (name) params.set("name", name);
    if (engineManufacturer) params.set("engine_manufacturer", engineManufacturer);
    try {
      setVessels(await listVessels(`?${params.toString()}`));
      setError(null);
    } catch {
      setError("Sorgu başarısız.");
    }
  }

  useEffect(() => {
    runSearch();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="p-6">
      <h1 className="mb-1 text-xl font-bold text-marinise-navy">Vessel Database</h1>
      <p className="mb-4 text-sm text-gray-500">Section 6 gelişmiş filtreleme (FAZ 1 alt kümesi: ad + ana makine markası).</p>

      <div className="mb-4 flex gap-3">
        <input
          placeholder="Gemi adı..."
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="rounded border border-gray-300 px-3 py-2 text-sm"
        />
        <input
          placeholder="Ana makine markası (örn. CAT)"
          value={engineManufacturer}
          onChange={(e) => setEngineManufacturer(e.target.value)}
          className="rounded border border-gray-300 px-3 py-2 text-sm"
        />
        <button
          onClick={runSearch}
          className="rounded bg-marinise-navy px-4 py-2 text-sm font-medium text-white hover:opacity-90"
        >
          Ara
        </button>
      </div>

      {error && <p className="text-sm text-red-600">{error}</p>}

      <table className="w-full border-collapse overflow-hidden rounded-lg bg-white text-sm shadow-sm">
        <thead className="bg-marinise-navy text-left text-white">
          <tr>
            <th className="px-3 py-2">Gemi Adı</th>
            <th className="px-3 py-2">Tip</th>
            <th className="px-3 py-2">Bayrak</th>
            <th className="px-3 py-2">Boy (m)</th>
            <th className="px-3 py-2">MMSI</th>
          </tr>
        </thead>
        <tbody>
          {vessels.map((v) => (
            <tr key={v.id} className="border-b border-gray-100 hover:bg-marinise-gray">
              <td className="px-3 py-2">
                <Link href={`/vessels/${v.id}`} className="font-medium text-marinise-navy hover:underline">
                  {v.name}
                </Link>
              </td>
              <td className="px-3 py-2">{v.vessel_type}</td>
              <td className="px-3 py-2">{v.flag ?? "-"}</td>
              <td className="px-3 py-2">{v.length_m ?? "-"}</td>
              <td className="px-3 py-2">{v.mmsi ?? "-"}</td>
            </tr>
          ))}
          {vessels.length === 0 && (
            <tr>
              <td colSpan={5} className="px-3 py-6 text-center text-gray-400">
                Sonuç bulunamadı.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
