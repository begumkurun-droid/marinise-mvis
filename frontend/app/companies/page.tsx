"use client";

import { useEffect, useState } from "react";
import { CompanyInfo, listCompanies } from "@/lib/api";

export default function CompanyDirectoryPage() {
  const [name, setName] = useState("");
  const [companies, setCompanies] = useState<CompanyInfo[]>([]);
  const [error, setError] = useState<string | null>(null);

  async function runSearch() {
    const params = new URLSearchParams();
    if (name) params.set("name", name);
    try {
      setCompanies(await listCompanies(`?${params.toString()}`));
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
      <h1 className="mb-1 text-xl font-bold text-marinise-navy">Company Directory</h1>
      <p className="mb-4 text-sm text-gray-500">
        Section 7 — gemi detay sayfasından "+ Şirket Ekle" ile kaydedilen owner/management şirketleri.
      </p>

      <div className="mb-4 flex gap-3">
        <input
          placeholder="Şirket adı..."
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="rounded border border-gray-300 px-3 py-2 text-sm"
        />
        <button onClick={runSearch} className="rounded bg-marinise-navy px-4 py-2 text-sm font-medium text-white hover:opacity-90">
          Ara
        </button>
      </div>

      {error && <p className="text-sm text-red-600">{error}</p>}

      <table className="w-full border-collapse overflow-hidden rounded-lg bg-white text-sm shadow-sm">
        <thead className="bg-marinise-navy text-left text-white">
          <tr>
            <th className="px-3 py-2">Şirket</th>
            <th className="px-3 py-2">Rol</th>
            <th className="px-3 py-2">Ülke</th>
            <th className="px-3 py-2">Web Sitesi</th>
            <th className="px-3 py-2">Genel E-posta</th>
          </tr>
        </thead>
        <tbody>
          {companies.map((c) => (
            <tr key={c.id} className="border-b border-gray-100 hover:bg-marinise-gray">
              <td className="px-3 py-2 font-medium">{c.name}</td>
              <td className="px-3 py-2">{c.role ?? "-"}</td>
              <td className="px-3 py-2">{c.country ?? "-"}</td>
              <td className="px-3 py-2">
                {c.website ? (
                  <a href={c.website} target="_blank" rel="noreferrer" className="text-marinise-orange underline">
                    {c.website}
                  </a>
                ) : (
                  "-"
                )}
              </td>
              <td className="px-3 py-2">{c.general_email ?? "-"}</td>
            </tr>
          ))}
          {companies.length === 0 && (
            <tr>
              <td colSpan={5} className="px-3 py-6 text-center text-gray-400">
                Henüz şirket kaydı yok. Gemi detay sayfasından ekleyebilirsiniz.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
