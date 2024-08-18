import React, {useEffect} from 'react';
import DocumentList from "./DocumentList";
import MainHeader from "./MainHeader";
import {Image} from './helpers/ImageHelper';
import './Home.css';

export default function Home() {
    return (
      <div className={"mainSection"}>
          <div className={"main-section-inner"}>
              {MainHeader()}
              {DocumentList()}
          </div>
      </div>
    )
}

