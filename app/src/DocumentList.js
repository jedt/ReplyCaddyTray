import React, {useEffect, useState} from 'react';
import {Image} from "./helpers/ImageHelper";
import './DocumentList.css';
function displayTags(tags) {
  // for each tags
  return tags.map(tag => {
    return (
      <span className={"tagWrapper"} key={tag}>
        {tag}
      </span>
    );
  });
}
export default function DocumentList() {
  const [documents, setDocuments] = useState([]);
  useEffect(() => {
    fetch('http://127.0.0.1:8971/api/data')
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(data => setDocuments(data))
      .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
      });
  }, []);

  return (
    <table className={"documentsTable"}>
      <thead>
        <tr>
            <th className={"table-icon-th"}>
                <div className={"table-icon"} style={{"width": "34px"}}></div>
            </th>
            <th>File Name</th>
            <th>Tags</th>
        </tr>
      </thead>
      <tbody>
      {documents.slice(0, 4).map(document => (
        <tr className={"rowItem"} key={document.file_name}>
            <td className={"table-icon-col"}>
                <div className={"table-icon-col-wrapper"}>
                    <span><Image height={20} src={"./images/document-icon.png"} /></span>
                </div>
            </td>
          <td>
              <div className={"table-filename-col"}>
                  <div className={"text-label"}>{document.file_name}</div>
                  <div>March 8, 1980</div>
              </div>
          </td>
          <td>
            {displayTags(document.tags)}
          </td>
        </tr>
      ))}
      </tbody>
    </table>
  );
};
