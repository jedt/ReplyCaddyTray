import {combineReducers} from '@reduxjs/toolkit';
import documentsReducer from './features/documents/documentsSlice';

const rootReducer = combineReducers({
  documents: documentsReducer
});

export default rootReducer;
