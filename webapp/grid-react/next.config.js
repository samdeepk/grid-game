/** @type {import('next').NextConfig} */
const API_PROXY_TARGET =
  process.env.NEXT_PUBLIC_API_PROXY_TARGET ||
  process.env.API_PROXY_TARGET ||
  'http://127.0.0.1:8000';

const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${API_PROXY_TARGET}/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;

