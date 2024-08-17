import React, {useEffect} from 'react';
import DocumentList from "./DocumentList";
import MainHeader from "./MainHeader";
import {Image} from './helpers/ImageHelper';

export default function Home() {
    return (
      <div className={"mainSection"}>
          {MainHeader()}
          {DocumentList()}
      </div>
    )
}

