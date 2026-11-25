"use client";

import { useEffect, useState } from "react";
import {
  COMPANY_ROLES,
  CompanyInfo,
  CompanyLinkInput,
  ResearchLinks,
  addCompanyLink,
  getResearchLinks,
} from "@/lib/api";

/**
 * Section 7/8 - Ownership & Management.
 *
 * There is no automatic "find the owner" button here on purpose: Equasis
 * and IMO GISIS both require the researcher's own free account and neither
 * publishes a confirmed automated-access policy (FAZ0 feasibility report).
 * So this panel gives quick entry links to search manually, and a short
 * form to save what's found - building MARINISE's own database over time.
 */
export default function CompanyResearchPanel({
  vesselId,
  companies,
  onSaved,
}: {
  vesselId: number;
  companies: CompanyInfo[];
  onSaved: () => void;
}) {
  const [links, setLinks] = useState<ResearchLinks | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState<CompanyLinkInput>({
    company_name: "",
    role: "yacht_management",
    website: "",
    general_email: "",
  });

  useEffect(() => {
    getResearchLinks(vesselId).then(setLinks).catch(() => undefined);
  }, [vesselId]);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (!form.company_name.trim()) return;
    setSaving(true);
    setError(null);
    try {
      await addCompanyLink(vesselId, { ...form, data_source: "Manuel araştırma" });
      setForm({ company_name: "", role: "yacht_management", website: "", general_email: "" });
      setShowForm(false);
      onSaved();
    } catch {
      setError("Kaydedilemedi.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="rounded-lg bg-white p-4 shadow-sm">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="font-semibold text-marinise-navy">Ownership & Management</h2>
        <button
          onClick={() => setShowForm((s) => !s)}
          className="rounded bg-marinise-navy px-3 py-1 text-xs font-medium text-white hover:opacity-90"
        >
          {showForm ? "Vazgeç" : "+ Şirket Ekle"}
        </button>
      </div>

      {companies.length === 0 && !showForm && (
        <p className="text-sm text-gray-400">Owner/management şirketi henüz tespit edilmedi.</p>
      )}

      <ul className="mb-3 space-y-2 text-sm">
        {companies.map((c) => (
          <li key={c.id + (c.role ?? "")} className="border-b border-gray-100 pb-2">
            <span className="font-medium">{c.name}</span>
            {c.role && <span className="ml-2 rounded bg-gray-100 px-2 py-0.5 text-xs">{c.role}</span>}
            {c.website && (
              <a href={c.website} target="_blank" className="ml-2 text-xs text-marinise-orange" rel="noreferrer">
                {c.website}
              </a>
            )}
            {c.general_email && <span className="ml-2 text-xs text-gray-400">{c.general_email}</span>}
          </li>
        ))}
      </ul>

      {showForm && (
        <form onSubmit={submit} className="mb-4 space-y-2 rounded border border-gray-200 bg-marinise-gray p-3">
          <input
            placeholder="Şirket adı *"
            required
            value={form.company_name}
            onChange={(e) => setForm({ ...form, company_name: e.target.value })}
            className="w-full rounded border border-gray-300 px-2 py-1.5 text-sm"
          />
          <select
            value={form.role}
            onChange={(e) => setForm({ ...form, role: e.target.value })}
            className="w-full rounded border border-gray-300 px-2 py-1.5 text-sm"
          >
            {COMPANY_ROLES.map((r) => (
              <option key={r.value} value={r.value}>
                {r.label}
              </option>
            ))}
          </select>
          <input
            placeholder="Web sitesi"
            value={form.website}
            onChange={(e) => setForm({ ...form, website: e.target.value })}
            className="w-full rounded border border-gray-300 px-2 py-1.5 text-sm"
          />
          <input
            placeholder="Genel e-posta (örn. info@...)"
            value={form.general_email}
            onChange={(e) => setForm({ ...form, general_email: e.target.value })}
            className="w-full rounded border border-gray-300 px-2 py-1.5 text-sm"
          />
          {error && <p className="text-xs text-red-600">{error}</p>}
          <button
            type="submit"
            disabled={saving}
            className="w-full rounded bg-marinise-orange py-1.5 text-sm font-semibold text-white hover:opacity-90 disabled:opacity-50"
          >
            {saving ? "Kaydediliyor…" : "Kaydet"}
          </button>
        </form>
      )}

      {links && (
        <div className="rounded border border-dashed border-gray-300 p-3 text-xs text-gray-600">
          <p className="mb-2">
            Elle araştırma için (her iki site de kendi ücretsiz hesabınızla giriş ister — IMO:{" "}
            <strong>{links.imo_number ?? "yok"}</strong>, MMSI: <strong>{links.mmsi ?? "-"}</strong>):
          </p>
          <div className="flex gap-2">
            <a
              href={links.equasis_url}
              target="_blank"
              rel="noreferrer"
              className="rounded bg-white px-2 py-1 font-medium text-marinise-navy underline"
            >
              Equasis'te Ara ↗
            </a>
            <a
              href={links.imo_gisis_url}
              target="_blank"
              rel="noreferrer"
              className="rounded bg-white px-2 py-1 font-medium text-marinise-navy underline"
            >
              IMO GISIS'te Ara ↗
            </a>
          </div>
        </div>
      )}
    </section>
  );
}
