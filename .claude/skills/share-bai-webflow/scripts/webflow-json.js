#!/usr/bin/env node
// JSON/text helpers for share-bai-webflow. Consolidates the JSON parsing/building
// this skill needs into a fixed script, so the Bash permission allowlist can
// scope to this script's invocation prefix instead of matching arbitrary `node -e`.
// No network calls here — all HTTP goes through scripts/webflow-http.sh.
const fs = require('fs');
const crypto = require('crypto');

const [, , cmd, ...args] = process.argv;

function readJson(path) {
  return JSON.parse(fs.readFileSync(path, 'utf8'));
}

function writeAccounts(path, acc) {
  fs.writeFileSync(path, JSON.stringify(acc, null, 2) + '\n');
}

switch (cmd) {
  case 'get-account-field': {
    // get-account-field <accounts-json-file> <site-key> <field>
    const [file, siteKey, field] = args;
    const acc = fs.existsSync(file) ? readJson(file) : {};
    const value = acc[siteKey] ? acc[siteKey][field] : undefined;
    console.log(value === undefined || value === null ? '' : value);
    break;
  }
  case 'save-token': {
    // save-token <accounts-json-file> <site-key> <token>
    const [file, siteKey, token] = args;
    let acc = {};
    if (fs.existsSync(file)) acc = readJson(file);
    acc[siteKey] = { ...acc[siteKey], token, token_saved_at: new Date().toISOString() };
    writeAccounts(file, acc);
    console.log('saved token for', siteKey);
    break;
  }
  case 'set-site': {
    // set-site <accounts-json-file> <site-key> <site_id> <collection_id> <field-body-slug> <field-image-slug-or-empty> <site-domain>
    const [file, siteKey, siteId, collectionId, fieldBody, fieldImage, siteDomain] = args;
    let acc = {};
    if (fs.existsSync(file)) acc = readJson(file);
    acc[siteKey] = {
      ...acc[siteKey],
      site_id: siteId,
      collection_id: collectionId,
      field_body: fieldBody,
      field_image: fieldImage || null,
      site_domain: siteDomain,
    };
    writeAccounts(file, acc);
    console.log('saved site config for', siteKey);
    break;
  }
  case 'md5-file': {
    // md5-file <local-file>  -- hex md5, used as fileHash when creating an asset
    const [file] = args;
    const buf = fs.readFileSync(file);
    console.log(crypto.createHash('md5').update(buf).digest('hex'));
    break;
  }
  case 'find-site-id': {
    // find-site-id <list-sites-response-json-file> <name-or-domain-substring>
    const [file, needle] = args;
    const r = readJson(file);
    const sites = r.sites || [];
    const match = sites.find(s =>
      (s.displayName || '').toLowerCase().includes(needle.toLowerCase()) ||
      (s.shortName || '').toLowerCase().includes(needle.toLowerCase()) ||
      (s.customDomains || []).some(d => (d.url || '').toLowerCase().includes(needle.toLowerCase()))
    );
    console.log(match ? JSON.stringify({ id: match.id, displayName: match.displayName, shortName: match.shortName }) : '');
    break;
  }
  case 'find-collection-id': {
    // find-collection-id <list-collections-response-json-file> <name-substring>
    const [file, needle] = args;
    const r = readJson(file);
    const collections = r.collections || [];
    const match = collections.find(c => (c.displayName || '').toLowerCase().includes((needle || '').toLowerCase()));
    console.log(match ? JSON.stringify({ id: match.id, displayName: match.displayName, slug: match.slug }) : '');
    break;
  }
  case 'find-field-slug': {
    // find-field-slug <collection-schema-json-file> <field-type>  -- e.g. RichText, Image
    const [file, fieldType] = args;
    const r = readJson(file);
    const fields = r.fields || [];
    const match = fields.find(f => f.type === fieldType);
    console.log(match ? match.slug : '');
    break;
  }
  case 'build-item-payload': {
    // build-item-payload <content-html-file> <title> <slug> <field-body-slug> <field-image-slug-or-empty> <image-hosted-url-or-empty> <out-file> [field-link-slug] [link-url]
    // field-link-slug/link-url: optional, for collections with a required Link field (e.g. AIG's "link" = source URL)
    const [contentFile, title, slug, fieldBody, fieldImage, imageUrl, outFile, fieldLink, linkUrl] = args;
    const content = fs.readFileSync(contentFile, 'utf8');
    const fieldData = { name: title, slug, [fieldBody]: content };
    if (fieldImage && imageUrl) fieldData[fieldImage] = { url: imageUrl };
    if (fieldLink && linkUrl) fieldData[fieldLink] = linkUrl;
    const payload = { isArchived: false, isDraft: false, fieldData };
    fs.writeFileSync(outFile, JSON.stringify(payload));
    console.log('written', outFile, fs.statSync(outFile).size, 'bytes');
    break;
  }
  case 'word-count': {
    // word-count <rich-text-html-file>
    const [file] = args;
    const html = fs.readFileSync(file, 'utf8');
    const text = html.replace(/<!--[\s\S]*?-->/g, '').replace(/<[^>]+>/g, ' ');
    console.log(text.trim().split(/\s+/).filter(Boolean).length);
    break;
  }
  case 'show-asset-hosted-url': {
    // show-asset-hosted-url <create-asset-response-json-file>
    const [file] = args;
    const r = readJson(file);
    console.log(r.hostedUrl || '');
    break;
  }
  case 'show-item-result': {
    // show-item-result <create-or-publish-response-json-file>
    const [file] = args;
    const r = readJson(file);
    console.log(JSON.stringify({
      id: r.id, isDraft: r.isDraft, lastPublished: r.lastPublished,
      slug: r.fieldData ? r.fieldData.slug : undefined,
      name: r.fieldData ? r.fieldData.name : undefined,
    }, null, 2));
    break;
  }
  case 'show-error': {
    // show-error <response-json-file>  -- Webflow error responses use {code, message}
    const [file] = args;
    try {
      const r = readJson(file);
      console.log(r.message || r.msg || JSON.stringify(r));
    } catch {
      console.log('(response is not valid JSON — see raw file)');
    }
    break;
  }
  default:
    console.error('webflow-json.js: unknown subcommand', cmd, '(expected: get-account-field|save-token|set-site|md5-file|find-site-id|find-collection-id|find-field-slug|build-item-payload|word-count|show-asset-hosted-url|show-item-result|show-error)');
    process.exit(1);
}
