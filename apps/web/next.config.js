const nextConfig = {
  output: "standalone",
  env: {
    NEXT_PUBLIC_API_BASE: process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000',
  },
  experimental: {
    outputFileTracingRoot: undefined,
  },
}

module.exports = nextConfig