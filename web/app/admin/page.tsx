"use client";
import { GithubAppInstallation } from "@/components/auth/GithubAppInstallationComponent";
import {GithubSignInComponent} from "@/components/auth/GithubSignInComponent"
import { SignInComponent } from "@/components/auth/SignInComponent";
import { Skeleton } from "@/components/ui/skeleton";
import { signIn, useSession, signOut } from 'next-auth/react';
import React, { useState, useEffect } from 'react';

interface Org {
    github_id: string, 
    organization_name: string

}

const App = () => {

    const { data: session, status } = useSession();
    const [githubId, setGithubId] = useState<string| undefined | null>(null);
    console.log(session)

    useEffect(() => {
        const fetchData = async () => {
          const apiUrl = process.env.NEXT_PUBLIC_API_URL;
          const url = apiUrl + "/retrieve_org";
    
          try {
            const requestOptions = {
              method: "POST", // Method type
              headers: {
                "Content-Type": "application/json" // Indicate JSON data being sent
              },
              // mode: "cors", // commented as it gives build error
              body: JSON.stringify({
                refresh_token: session?.refreshToken,
                access_token: session?.accessToken,
    
              }) // Convert the JavaScript object to a JSON string
            };
            const response = await fetch(url, requestOptions);
    
            console.log(response);
    
            if (response.ok) {
              const responseObj : Org = await response.json()
              console.log(responseObj)
              if(responseObj.github_id !== undefined) {
                setGithubId(responseObj.github_id)
              }

    
            }
          } catch (error) {
            throw new Error("e")
          }
        }
        if (status === "authenticated") {
          fetchData()
        }
      }, [status])

    return (

      <div>
        { githubId !== undefined && githubId !== null ?
        <GithubAppInstallation></GithubAppInstallation>:
        status === "unauthenticated"?
        <SignInComponent></SignInComponent>:
        status === "authenticated" && githubId === undefined ?
          <GithubSignInComponent></GithubSignInComponent>
          :
        <Skeleton></Skeleton>
        }
      </div>
    );
  };
  export default App;