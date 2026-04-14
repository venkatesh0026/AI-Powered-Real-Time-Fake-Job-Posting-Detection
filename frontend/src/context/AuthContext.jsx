import { createContext, useContext, useEffect, useState } from 'react'
import { supabase } from '../lib/supabase'

const defaultValue = {
    signUp: async () => Promise.reject('AuthProvider not initialized'),
    signIn: async () => Promise.reject('AuthProvider not initialized'),
    signOut: async () => Promise.reject('AuthProvider not initialized'),
    user: null,
}

const AuthContext = createContext(defaultValue)

export const useAuth = () => useContext(AuthContext)

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        // Check if there's a mock user in localStorage
        const mockUser = localStorage.getItem('mock_user')
        if (mockUser) {
            setUser(JSON.parse(mockUser))
        }

        if (!supabase) {
            setLoading(false)
            return
        }

        // Check active sessions and sets the user
        supabase.auth.getSession().then(({ data: { session } }) => {
            setUser(session?.user ?? null)
            setLoading(false)
        })

        // Listen for changes on auth state (logged in, signed out, etc.)
        const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
            setUser(session?.user ?? null)
            setLoading(false)
        })

        return () => subscription?.unsubscribe()
    }, [])

    const value = {
        signUp: (data) => supabase.auth.signUp(data),
        signIn: (data) => supabase.auth.signInWithPassword(data),
        signOut: () => {
            localStorage.removeItem('mock_user')
            return supabase.auth.signOut()
        },
        user,
    }

    return (
        <AuthContext.Provider value={value}>
            {!loading && children}
        </AuthContext.Provider>
    )
}
