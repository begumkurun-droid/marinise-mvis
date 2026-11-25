"use client";

import { Suspense } from "react";
import { useSearchParams } from "next/navigation";

function SoonContent() {
  const params = useSearchParams();
  const from = params.get("from") ?? "Bu modül";

  return (
    <div className="flex h-full flex-col items-center justify-center p-10 text-center">
      <h1 className="text-xl font-semibold text-marinise-navy">{from}</h1>
      <p className="mt-2 max-w-md text-sm text-gray-500">
        Bu modül FAZ 0 fizibilite raporunda planlanan sonraki geliştirme fazlarından birinde
        (bkz. PROJECT_PLAN.md) uygulanacak. Şu anda FAZ 1 kapsamındaki Executive Dashboard,
        Live Vessel Map ve Vessel Database modülleri aktif.
      </p>
    </div>
  );
}

export default function SoonPage() {
  return (
    <Suspense fallback={null}>
      <SoonContent />
    </Suspense>
  );
}
