#!/usr/bin/env node
// JSON helpers for google-sheets-social. Consolidates the JSON parsing/building
// this skill needs into a fixed script, so the Bash permission allowlist can
// scope to this script's invocation prefix instead of matching arbitrary `node -e`.
const fs = require('fs');

const [, , cmd, ...args] = process.argv;

function readJson(path) {
  return JSON.parse(fs.readFileSync(path, 'utf8'));
}

function writeAccounts(path, acc) {
  fs.writeFileSync(path, JSON.stringify(acc, null, 2) + '\n');
}

switch (cmd) {
  case 'get-account-field': {
    // get-account-field <accounts-json-file> <sheet-key> <field>
    const [file, sheetKey, field] = args;
    const acc = readJson(file);
    const value = acc[sheetKey] ? acc[sheetKey][field] : undefined;
    console.log(value === undefined || value === null ? '' : value);
    break;
  }
  case 'set-client': {
    // set-client <accounts-json-file> <sheet-key> <client_id> <client_secret> <spreadsheet_id> <sheet_name>
    const [file, sheetKey, clientId, clientSecret, spreadsheetId, sheetName] = args;
    let acc = {};
    if (fs.existsSync(file)) acc = readJson(file);
    acc[sheetKey] = {
      ...acc[sheetKey],
      client_id: clientId,
      client_secret: clientSecret,
      spreadsheet_id: spreadsheetId,
      sheet_name: sheetName,
    };
    writeAccounts(file, acc);
    console.log('saved client for', sheetKey);
    break;
  }
  case 'save-tokens': {
    // save-tokens <accounts-json-file> <sheet-key> <token-response-json-file>
    const [file, sheetKey, tokenRespFile] = args;
    const acc = readJson(file);
    const resp = readJson(tokenRespFile);
    if (!resp.access_token) {
      console.error('save-tokens: response has no access_token');
      process.exit(1);
    }
    if (!resp.refresh_token && !(acc[sheetKey] && acc[sheetKey].refresh_token)) {
      console.error('save-tokens: response has no refresh_token and none stored yet — re-run OAuth with access_type=offline&prompt=consent');
      process.exit(1);
    }
    acc[sheetKey] = {
      ...acc[sheetKey],
      access_token: resp.access_token,
      refresh_token: resp.refresh_token || acc[sheetKey].refresh_token,
      token_type: resp.token_type || 'Bearer',
      expires_in_seconds: resp.expires_in || 3600,
      obtained_at: new Date().toISOString(),
    };
    writeAccounts(file, acc);
    console.log('saved tokens for', sheetKey, 'has refresh_token:', !!acc[sheetKey].refresh_token);
    break;
  }
  case 'save-refreshed-access-token': {
    // save-refreshed-access-token <accounts-json-file> <sheet-key> <refresh-response-json-file>
    // Google refresh responses normally do NOT include a new refresh_token — keep the stored one.
    const [file, sheetKey, refreshRespFile] = args;
    const acc = readJson(file);
    const resp = readJson(refreshRespFile);
    if (!resp.access_token) {
      console.error('save-refreshed-access-token: response has no access_token (refresh_token may be revoked)');
      process.exit(1);
    }
    acc[sheetKey] = {
      ...acc[sheetKey],
      access_token: resp.access_token,
      expires_in_seconds: resp.expires_in || 3600,
      obtained_at: new Date().toISOString(),
    };
    writeAccounts(file, acc);
    console.log('refreshed access_token for', sheetKey);
    break;
  }
  case 'parse-sheet-data': {
    // parse-sheet-data <get-sheet-data-response-json-file> <out-file> [header-row-number]
    // header-row-number (1-based, default 1): for sheets whose real header is not
    // row 1 (e.g. a merged group-label row sits above it); rows above it are skipped.
    // Flattens the raw Sheets API grid into: headers (index/text/hyperlink) + rows
    // (1-based real sheet row index, "checked" from the header fuzzy-matching
    // "duyệt"/"approve"/"publish", and a text-value map keyed by header).
    const [file, outFile, headerRowArg] = args;
    const headerRowIdx = Math.max(0, (Number(headerRowArg) || 1) - 1);
    const resp = readJson(file);
    const sheet = resp.sheets && resp.sheets[0];
    const rowData = (sheet && sheet.data && sheet.data[0] && sheet.data[0].rowData) || [];
    if (!rowData.length) {
      console.error('parse-sheet-data: response has no rowData — check spreadsheet_id/sheet_name and that the range is not empty');
      process.exit(1);
    }
    const cellText = (cell) => (cell ? (cell.formattedValue ?? '') : '');
    const cellHyperlink = (cell) => (cell && cell.hyperlink) || null;

    const headerRow = (rowData[headerRowIdx] && rowData[headerRowIdx].values) || [];
    const headers = headerRow.map((cell, index) => ({
      index,
      text: cellText(cell).trim(),
      hyperlink: cellHyperlink(cell),
    }));

    const checkboxHeaderIndex = headers.findIndex((h) =>
      /duyệt|duyet|approve|publish/i.test(h.text)
    );

    const rows = [];
    for (let i = headerRowIdx + 1; i < rowData.length; i++) {
      const cells = rowData[i].values || [];
      if (!cells.length) continue;
      const values = {};
      headers.forEach((h) => {
        if (!h.text) return;
        values[h.text] = cellText(cells[h.index]);
      });
      const hasAnyValue = Object.values(values).some((v) => v !== '');
      if (!hasAnyValue) continue;
      rows.push({
        rowIndex: i + 1, // 1-based real sheet row number
        checked: checkboxHeaderIndex === -1 ? null : cellText(cells[checkboxHeaderIndex]).trim().toUpperCase() === 'TRUE',
        values,
      });
    }

    const out = {
      sheetTitle: sheet.properties && sheet.properties.title,
      headers,
      checkboxHeaderText: checkboxHeaderIndex === -1 ? null : headers[checkboxHeaderIndex].text,
      rows,
    };
    fs.writeFileSync(outFile, JSON.stringify(out, null, 2));
    console.log('written', outFile, '-', headers.length, 'headers,', rows.length, 'data rows, checkbox column:', out.checkboxHeaderText || 'NOT FOUND');
    break;
  }
  case 'build-a1-range': {
    // build-a1-range <sheet_name> <column-letter-or-index> <row-number>
    // Prints an A1-notation range like 'Share social'!F5 — sheet names with
    // spaces must be single-quoted per A1 notation; column may be given as a
    // letter (F) or a 0-based index (5 -> F).
    const [sheetName, column, row] = args;
    let colLetter = column;
    if (/^\d+$/.test(column)) {
      let n = Number(column) + 1; // 0-based index -> 1-based
      let letters = '';
      while (n > 0) {
        const rem = (n - 1) % 26;
        letters = String.fromCharCode(65 + rem) + letters;
        n = Math.floor((n - 1) / 26);
      }
      colLetter = letters;
    }
    const needsQuoting = /[^A-Za-z0-9_]/.test(sheetName);
    const safeSheetName = needsQuoting ? `'${sheetName.replace(/'/g, "''")}'` : sheetName;
    console.log(`${safeSheetName}!${colLetter}${row}`);
    break;
  }
  case 'build-update-cell-body': {
    // build-update-cell-body <value> <out-file>
    const [value, outFile] = args;
    fs.writeFileSync(outFile, JSON.stringify({ values: [[value]] }));
    console.log('written', outFile);
    break;
  }
  case 'show-update-result': {
    // show-update-result <update-response-json-file>
    const [file] = args;
    const r = readJson(file);
    console.log(JSON.stringify({
      updatedRange: r.updatedRange,
      updatedCells: r.updatedCells,
      error: r.error,
    }, null, 2));
    break;
  }
  default:
    console.error('sheets-json.js: unknown subcommand', cmd, '(expected: get-account-field|set-client|save-tokens|save-refreshed-access-token|parse-sheet-data|build-a1-range|build-update-cell-body|show-update-result)');
    process.exit(1);
}
