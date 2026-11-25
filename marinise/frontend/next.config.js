/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Section 18: "Sistem arama motorlarında indekslenmemelidir."
  async headers() {
    return [
      {
        source: "/:path*",
        headers: [{ key: "X-Robots-Tag", value: "noindex, nofollow" }],
      },
    ];
  },
};

module.exports = nextConfig;
