// types/next-auth.d.ts
import NextAuth from "next-auth";
import { JWT } from "next-auth/jwt";

// Extend the User model if you are also customizing it
declare module "next-auth" {
  interface Session {
    accessToken?: string;
    refreshToken?: string;
    googleToken?: string;
  }
}

declare module "next-auth/jwt" {
  interface JWT {
    accessToken?: string;
    refreshToken?: string;
  }
}
