import React from 'react';
import ReactDOM from 'react-dom/client';
import Dashboard from "./Dashboard";
import Home from "./Home";
import Settings from "./Settings";
import ErrorPage from "./error-page";
import store from './store';
import {Provider} from 'react-redux';

import {
  createBrowserRouter,
  RouterProvider,
} from "react-router-dom";
import './index.css';
//import App from './App';
import reportWebVitals from './reportWebVitals';

const router = createBrowserRouter([
  {
    path: "/",
    element: <Dashboard/>,
    errorElement: <ErrorPage />,
    children: [
      {
        index: true,
        element: <Home />,
      },
      {
        path: "settings",
        element: <Settings />,
      }
    ]
  },
]);


const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <Provider store={store}>
    <RouterProvider router={router} />
  </Provider>
);


// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
