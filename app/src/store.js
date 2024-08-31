import { configureStore } from "@reduxjs/toolkit";
import { documentsApi } from "./features/documents/documentsApi";
import documentsReducer from "./features/documents/documentsSlice";

const store = configureStore({
  reducer: {
    documents: documentsReducer,
    [documentsApi.reducerPath]: documentsApi.reducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(documentsApi.middleware),
});

export default store;
