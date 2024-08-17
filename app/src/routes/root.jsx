import React from "react";
import { Outlet } from "react-router-dom";

function Root() {
  return (
    <div>
      <h2>Parent Component</h2>
      {/* This will render the child route */}
      <Outlet />
    </div>
  );
}

export default Root;
