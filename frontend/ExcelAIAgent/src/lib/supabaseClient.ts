import { createClient } from '@supabase/supabase-js'
import { getSupabaseConfig } from '../config/supabase'

// Get Supabase configuration
const { url: supabaseUrl, anonKey: supabaseAnonKey } = getSupabaseConfig()

// Create Supabase client
export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    // Enable automatic session refresh
    autoRefreshToken: true,
    // Persist session in localStorage
    persistSession: true,
    // Detect session in URL (for email confirmations)
    detectSessionInUrl: true
  }
})
