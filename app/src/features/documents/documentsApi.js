import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

export const documentsApi = createApi({
  reducerPath: "documentsApi",
  baseQuery: fetchBaseQuery({ baseUrl: "http://127.0.0.1:8971/api/" }),
  endpoints: (builder) => ({
    fetchDocuments: builder.query({
      query: () => "data",
    }),
  }),
});

export const { useFetchDocumentsQuery } = documentsApi;
