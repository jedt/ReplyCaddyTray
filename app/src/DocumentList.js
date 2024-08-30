import React, {useEffect, useState} from 'react';
import {Image} from "./helpers/ImageHelper";
import './DocumentList.css';

// Define an asynchronous function
async function fetchData(url) {
    try {
        const response = await fetch(url);

        // Check if the response is ok (status code 200-299)
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        // Use await to pause the execution until the promise returned by response.json() is resolved
        const data = await response.json();

        // Log the data to the console or process it as needed
        console.log(data);

        // Return the data if needed
        return data;
    } catch (error) {
        // Handle any errors that occur during the fetch
        console.error('Error fetching data:', error);
    }
}

function displayTags(tags) {
  if (!tags) {
    return (<div />)
  }
  else {
    return tags.map(tag => {
      return (
        <span className={"tagWrapper"} key={tag}>
          {tag}
        </span>
      );
    });
  }
}
export default function DocumentList() {
  const [documents, setDocuments] = useState([]);
  useEffect(() => {
    (async () => {
      try {

        const fetch_headers = new Headers();
        fetch_headers.append("Content-Type", "application/json");
        const data = await fetch('http://127.0.0.1:8971/api/data', {
          headers: fetch_headers,
        });
        const newDocuments = await data.json();
        setDocuments(newDocuments);
      }
      catch (error) {
        console.log(error)
      }
    })();
  }, []);

  if (documents.length === 0) {
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

        </tbody>
      </table>
    )
  }

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
              <span><Image height={20} src={"./images/document-icon.png"}/></span>
            </div>
          </td>
          <td>
            <div className={"table-filename-col"}>
              <div className={"text-label"}>{document.file_name}</div>
              <div>{document.created_at}</div>
            </div>
          </td>
          <td>
            {displayTags(document.tags)}
          </td>
        </tr>
      ))}
      </tbody>
    </table>
  )
};
