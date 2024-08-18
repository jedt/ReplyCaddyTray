import React, {useEffect, useState} from 'react';
import './Settings.css';
import {Image} from "./helpers/ImageHelper";
import {useNavigate} from "react-router-dom";

function Settings() {
  const [documentsFilePath, setDocumentsFilePath] = useState({});
  const [downloadsFilePath, setDownloadsFilePath] = useState({});
  const navigate = useNavigate();

  useEffect(() => {
    fetch('http://127.0.0.1:8971/api/settings')
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(data => {
        try {
          setDocumentsFilePath(data.folders.documents);
          setDownloadsFilePath(data.folders.downloads);
        }
        catch (e) {
          console.error('There was a problem with the fetch operation:', e);
        }
      })
      .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
      });
  }, []);

  return (
    <div className={"mainSection"}>
      <div className={"settings"}>
        <div className={"mainSectionHeader"}>
          <div className={"toolbarItem"}>
            <button onClick={() => navigate(-1)}>
              <div className={"backWrapper"}>
                <Image height={10} src={"./images/back-icon.png"} />
              </div>
              <div className={"toolbarItemText"}>
                <span>Back</span>
              </div>
            </button>
          </div>
          <div className={"titleSection"}>
            <div className={"title"}>Settings</div>
            <div className={"caption"}>Manage your settings</div>
          </div>
          <div className={"bodySection"}>
            <form className={"settingsForm"} action="">
              <div className={"formItem"}>
                <label htmlFor="documentsPath">Documents Path:</label>
                <div className={"input-text-wrapper"}>
                  <input type="text" id="documentsPath" name="documentsPath" value={documentsFilePath} />
                </div>
              </div>
              <div className={"formItem"}>
                <label htmlFor="downloadsPath">Downloads Path:</label>
                <div className={"input-text-wrapper"}>
                  <input type="text" id="downloadsPath" name="downloadsPath" value={downloadsFilePath} />
                </div>
              </div>
              <div className={"formActionRow"}>
                <button type="submit">Save</button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Settings;
