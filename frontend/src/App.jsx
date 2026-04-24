import React, { useEffect } from "react";
import AppRoutes from "./routes";
import { initConnectionCheck } from "./utils/connectionTest";

const App = () => {
  useEffect(() => {
    // Check backend connection on app load
    initConnectionCheck();
  }, []);

  return (
    <div>
      <AppRoutes />
    </div>
  );
};

export default App;