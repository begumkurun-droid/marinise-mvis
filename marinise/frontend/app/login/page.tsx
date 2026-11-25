"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { login } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await login(email, password);
      router.push("/");
    } catch {
      setError("E-posta veya şifre hatalı.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex h-full items-center justify-center bg-marinise-gray">
      <form onSubmit={onSubmit} className="w-80 rounded-lg bg-white p-8 shadow-md">
        <h1 className="mb-1 text-lg font-bold text-marinise-navy">MARINISE® MVIS</h1>
        <p className="mb-6 text-sm text-gray-500">Vessel Intelligence System</p>

        <label className="mb-1 block text-sm font-medium text-gray-700">E-posta</label>
        <input
          type="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="mb-4 w-full rounded border border-gray-300 px-3 py-2 text-sm focus:border-marinise-orange focus:outline-none"
        />

        <label className="mb-1 block text-sm font-medium text-gray-700">Şifre</label>
        <input
          type="password"
          required
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="mb-4 w-full rounded border border-gray-300 px-3 py-2 text-sm focus:border-marinise-orange focus:outline-none"
        />

        {error && <p className="mb-3 text-sm text-red-600">{error}</p>}

        <button
          type="submit"
          disabled={loading}
          className="w-full rounded bg-marinise-orange py-2 text-sm font-semibold text-white hover:opacity-90 disabled:opacity-50"
        >
          {loading ? "Giriş yapılıyor..." : "Giriş Yap"}
        </button>
      </form>
    </div>
  );
}
