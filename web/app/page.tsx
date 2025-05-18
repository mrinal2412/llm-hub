// webv2/app/page.tsx

"use client";

import SearchHome from "@/components/search/SearchHome";
import ProjectsGrid from "@/components/projects/ProjectGrid";
import DatadogTracker from "@/monitoring/DatadogTracker";
import { store } from "@/redux/store/store";
import { Provider } from "react-redux";

const App = () => {
  return (
    <Provider store={store}>
      <DatadogTracker></DatadogTracker>
      <ProjectsGrid></ProjectsGrid>
    </Provider>
  );
};
export default App;
