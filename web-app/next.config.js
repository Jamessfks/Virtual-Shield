/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable standalone output for Docker
  output: 'standalone',
  
  // Image optimization
  images: {
    domains: [],
  },
  
  // Production optimizations
  swcMinify: true,
  reactStrictMode: true,
}

module.exports = nextConfig
