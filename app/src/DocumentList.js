import React, { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useFetchDocumentsQuery } from "./features/documents/documentsApi";
import { setDocuments } from "./features/documents/documentsSlice";
import { Image } from "./helpers/ImageHelper";
import "./DocumentList.css";

function displayTags(tags) {
  if (!tags) {
    return <div />;
  } else {
    return tags.map((tag) => {
      return (
        <span className={"tagWrapper"} key={tag}>
          {tag}
        </span>
      );
    });
  }
}
export default function DocumentList() {
  const dispatch = useDispatch();
  const { data: documents = [], error, isLoading } = useFetchDocumentsQuery();

  useEffect(() => {
    if (documents.length > 0) {
      dispatch(setDocuments(documents));
    }
  }, [documents, dispatch]);

  if (documents.length === 0) {
    return (
      <table className={"documentsTable"}>
        <thead>
          <tr>
            <th className={"table-icon-th"}>
              <div className={"table-icon"} style={{ width: "34px" }}></div>
            </th>
            <th>File Name</th>
            <th>Tags</th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    );
  }

  return (
    <table className={"documentsTable"}>
      <thead>
        <tr>
          <th className={"table-icon-th"}>
            <div className={"table-icon"} style={{ width: "34px" }}></div>
          </th>
          <th>File Name</th>
          <th>Tags</th>
        </tr>
      </thead>
      <tbody>
        {documents.slice(0, 4).map((document) => (
          <tr className={"rowItem"} key={document.file_name}>
            <td className={"table-icon-col"}>
              <div className={"table-icon-col-wrapper"}>
                <span>
                  <Image height={20} src={"./images/document-icon.png"} />
                </span>
              </div>
            </td>
            <td>
              <div className={"table-filename-col"}>
                <div className={"text-label"}>{document.file_name}</div>
                <div>{document.created_at}</div>
              </div>
            </td>
            <td>{displayTags(document.tags)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
