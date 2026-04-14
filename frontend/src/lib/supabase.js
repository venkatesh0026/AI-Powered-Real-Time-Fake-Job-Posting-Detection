import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

// Create a dummy client if credentials are not configured
export const supabase = (supabaseUrl && supabaseAnonKey) 
  ? createClient(supabaseUrl, supabaseAnonKey)
  : {
      // Mock auth object for demo/testing
      auth: {
        getSession: async () => {
          const mockUser = localStorage.getItem('mock_user')
          if (mockUser) {
            const user = JSON.parse(mockUser)
            return {
              data: {
                session: {
                  user: user,
                  access_token: 'mock_token_' + user.id
                }
              }
            }
          }
          return { data: { session: null } }
        },
        onAuthStateChange: () => ({ data: { subscription: { unsubscribe: () => {} } } }),
        signUp: async ({ email, password }) => {
          // Mock signup - just store user in localStorage
          if (!email || !password) {
            return { data: null, error: new Error('Email and password required') }
          }
          const mockUserId = Math.random().toString()
          const mockUser = { email, id: mockUserId }
          localStorage.setItem('mock_user', JSON.stringify(mockUser))
          return { data: { user: mockUser }, error: null }
        },
        signInWithPassword: async ({ email, password }) => {
          // Mock login - accept any email/password combination
          if (!email || !password) {
            return { data: null, error: new Error('Email and password required') }
          }
          const mockUserId = Math.random().toString()
          const mockUser = { email, id: mockUserId }
          localStorage.setItem('mock_user', JSON.stringify(mockUser))
          return { data: { user: mockUser }, error: null }
        },
        signOut: async () => {
          localStorage.removeItem('mock_user')
          return { error: null }
        }
      }
    }




