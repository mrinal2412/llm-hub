import { access } from "fs";
import NextAuth from "next-auth";
import GoogleProvider from "next-auth/providers/google";
import GithubProvider from "next-auth/providers/github";
import { cookies } from "next/headers";

// TODO: Got type error for NextApiRequest and NextApiResponse. So not using them for now.
import type { NextApiRequest, NextApiResponse } from "next";

console.log(process.env.CLIENT_ID);

async function auth(req: any, res: any) {
  return await NextAuth(req, res, {
    providers: [
      GithubProvider({
        clientId: process.env.GITHUB_CLIENT_ID as string,
        clientSecret: process.env.GITHUB_CLIENT_SECRET as string
      }),
      GoogleProvider({
        clientId: process.env.CLIENT_ID as string,
        clientSecret: process.env.CLIENT_SECRET as string,

        authorization: {
          params: {
            scope: "openid email profile https://www.googleapis.com/auth/drive.readonly",
            access_type: "offline", // Request a refresh token.
            prompt: "consent" // Force a prompt for consent to ensure a refresh token is always returned.
          }
        }
      })
    ],
    secret: process.env.NEXTAUTH_SECRET,
    callbacks: {
      async jwt({ token, account }) {
        // Persist the OAuth access_token to the token right after signin
        
        console.log("Accccount")
        console.log(account)
        console.log(token)
        console.log(cookies().get("google_auth_session"))
        if (account?.provider === "github") {

          if (cookies().get("google_auth_session") !== undefined) {
            let sessionStr = cookies().get("google_auth_session")?.value;
            if (sessionStr !== undefined)
              var sessionObj = JSON.parse(sessionStr);
            const data = {
              // Your data here, for example:
              refresh_token: sessionObj.refreshToken,
              access_token: sessionObj.accessToken,
              github_access_token: account.access_token
            };
            const apiUrl = process.env.NEXT_PUBLIC_API_URL + "/link_github";
            try {
              // Make a POST request to your API
              const response = await fetch(apiUrl, {
                method: "POST",
                headers: {
                  "Content-Type": "application/json"
                  // If you need to pass the token, though typically for user-specific actions rather than during sign-in
                  // 'Authorization': `Bearer ${token.accessToken}`,
                },
                body: JSON.stringify(data)
              });

              if (response.status === 409) {
                console.log("response stsatus " + response.status);
              } else if (!response.ok) {
                throw new Error(`Error: ${response.statusText}`);
              }

              const responseData = await response.json();
              console.log(responseData);
            } catch (error) {
              console.error("Error calling the API", error);
              throw error;
            }
          }
          token.provider = "github";
        }

        if (account?.provider === "google") {
          console.log(account);
          console.log("access token " + account.refresh_token);
          token.accessToken = account.id_token;
          token.refreshToken = account.refresh_token;
          // Define your API endpoint
          const apiUrl = process.env.NEXT_PUBLIC_API_URL + "/onboard_user";
          // const apiUrl = "http://localhost:8000/setup_org";

          // Prepare the data you want to send
          const data = {
            // Your data here, for example:
            refresh_token: account.refresh_token,
            access_token: account.id_token
          };

          token.provider = "google";
          // token.providers= {
          //   googleAccessToken: account.access_token,
          //   googleRefreshToken: account.refresh_token,
          // };
          console.log("data : " + JSON.stringify(data));

          try {
   
            const response = await fetch(apiUrl, {
              method: "POST",
              headers: {
                "Content-Type": "application/json"
                // If you need to pass the token, though typically for user-specific actions rather than during sign-in
                // 'Authorization': `Bearer ${token.accessToken}`,
              },
              body: JSON.stringify(data)
            });

            if (response.status === 409) {
              console.log("response stsatus " + response.status);
            } else if (!response.ok) {
              throw new Error(`Error: ${response.statusText}`);
            }

            const responseData = await response.json();
            console.log(responseData);
          } catch (error) {
            console.error("Error calling the API", error);
            throw error;
          }
        }
        return token;
      },

      async session({ session, token, user }) {
        // Send properties to the client, like an access_token from a provider.
        // console.log("did it come hereee " + token.accessToken)
        // console.log("did it come hereee " + token.refreshToken)

        if (cookies().get("google_auth_session")?.value !== undefined) {
          let sessionStr = cookies().get("google_auth_session")?.value;
          if (sessionStr !== undefined) return JSON.parse(sessionStr);
        }

        if (token.provider === "google") {
          session.accessToken = token.accessToken;
          session.refreshToken = token.refreshToken;
          session.googleToken = "google";
          cookies().set("google_auth_session", JSON.stringify(session));
        }

        return session;
      }
    }
  });
}
// const handler =

// export { handler as GET, handler as POST };

export { auth as GET, auth as POST };
