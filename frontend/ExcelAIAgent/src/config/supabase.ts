// Supabase configuration for Excel add-in
// This file provides the Supabase configuration that works in both browser and Excel environments

// Replace these with your actual Supabase credentials

export const SUPABASE_CONFIG = {
  url:'https://bjscdnchhnpstkbcmpku.supabase.co' ,  // ← Replace with your actual Supabase URL
  anonKey: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJqc2NkbmNoaG5wc3RrYmNtcGt1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTU4MjM2MjMsImV4cCI6MjA3MTM5OTYyM30.oEUL-IZnZ-Zi70Iy-sKQLJi23YbsmSEk9QCXQ_D2GFo'                     // ← Replace with your actual anon key
}

// You can also set these via environment variables if available
export const getSupabaseConfig = () => {
  // Try to get from environment variables first
  const url = (typeof process !== 'undefined' && process.env?.REACT_APP_SUPABASE_URL) || SUPABASE_CONFIG.url
  const anonKey = (typeof process !== 'undefined' && process.env?.REACT_APP_SUPABASE_ANON_KEY) || SUPABASE_CONFIG.anonKey
  
  return {
    url,
    anonKey
  }
}
