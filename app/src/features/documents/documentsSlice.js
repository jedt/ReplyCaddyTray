import {createSlice} from '@reduxjs/toolkit';

const documentsSlice = createSlice({
  name: 'documents',
  initialState: [],
  reducers: {
    setDocuments(state, action) {
      return action.payload;
    }
  }
})


export const {setDocuments} = documentsSlice.actions;
export default documentsSlice.reducer;
