
import {
    Card,
    CardContent,
    CardDescription,
    CardFooter,
    CardHeader,
    CardTitle,
} from "@/components/ui/card"

import { signIn, useSession, signOut } from 'next-auth/react';
import { Button } from '../ui/button';

export const SignInComponent: React.FC = () => {

    const handleSignIn = () => {
        console.log("/")
        // Custom logic before signIn, if needed
        signIn('google', { callbackUrl: "/" }); // Specify the provider and optionally a redirect URL
    };

    return (

        <div>
            <div className="container mx-auto p-4">
                <div className="mt-8 mb-24"> {/* Increased top and bottom margins */}
                </div>

                <div className="grid grid-cols-4 gap-3 pt-3"> {/* Added top padding */}
                <div className="col-span-1 md:col-span-1 md:col-start-2"> {/* Makes the card take up one column and start in the third column on medium screens and larger */}
        
                    <Card className="w-[600px]">
                        <CardHeader>
                            <CardTitle> You need to login to start tracking your projects</CardTitle>
                            <CardDescription>  <Button className="bg-blue-200 rounded" onClick={handleSignIn}>Sign in with Google</Button> </CardDescription>
                        </CardHeader>
                    </Card>
                    </div>
                </div>
            </div>
        </div>

    )
}