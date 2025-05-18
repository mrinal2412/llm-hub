// webv2/socket/webSocket.ts

import { useEffect } from "react";

const useWebSocketConnection = () => {
  useEffect(() => {
    const socket = new WebSocket(
      process.env.NEXT_PUBLIC_WEBSOCKET_URL as string
    );

    socket.onopen = () => {
      console.log("WebSocket Connected");
    };

    socket.onmessage = (event) => {
      // Handle incoming messages
      console.log("Message from server ", event.data);
    };

    socket.onclose = () => {
      console.log("WebSocket Disconnected");
    };

    return () => {
      socket.close();
    };
  }, []);

  return null; // This hook does not need to return anything
};

export default useWebSocketConnection;
