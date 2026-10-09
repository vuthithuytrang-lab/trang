#!/usr/bin/env node
// JSON/Ricos helpers for share-bai-wix. Consolidates the JSON parsing/building
// this skill needs into a fixed script, so the Bash permission allowlist can
// scope to this script's invocation prefix instead of matching arbitrary `node -e`.
const fs = require('fs');
const crypto = require('crypto');

const [, , cmd, ...args] = process.argv;

function readJson(path) {
  return JSON.parse(fs.readFileSync(path, 'utf8'));
}

function writeAccounts(path, acc) {
  fs.writeFileSync(path, JSON.stringify(acc, null, 2) + '\n');
}

function nodeId() {
  return crypto.randomBytes(6).toString('hex');
}

switch (cmd) {
  case 'get-account-field': {
    // get-account-field <accounts-json-file> <site-key> <field>
    const [file, siteKey, field] = args;
    const acc = readJson(file);
    const value = acc[siteKey] ? acc[siteKey][field] : undefined;
    console.log(value === undefined || value === null ? '' : value);
    break;
  }
  case 'set-credentials': {
    // set-credentials <accounts-json-file> <site-key> <api_key> <account_id> <site_id> [member_id]
    const [file, siteKey, apiKey, accountId, siteId, memberId] = args;
    let acc = {};
    if (fs.existsSync(file)) acc = readJson(file);
    acc[siteKey] = {
      ...acc[siteKey],
      api_key: apiKey,
      account_id: accountId,
      site_id: siteId,
      ...(memberId ? { member_id: memberId } : {}),
    };
    writeAccounts(file, acc);
    console.log('saved credentials for', siteKey);
    break;
  }
  case 'save-member-id': {
    // save-member-id <accounts-json-file> <site-key> <members-response-json-file>
    // Picks the first member returned (typically the site owner) and stores it —
    // this only needs to run once per site, not on every run.
    const [file, siteKey, membersRespFile] = args;
    const acc = readJson(file);
    const resp = readJson(membersRespFile);
    const member = resp.members && resp.members[0];
    if (!member || !member.id) {
      console.error('save-member-id: response has no members — check the site has at least one member/owner, or that site_id/api_key are correct');
      process.exit(1);
    }
    acc[siteKey] = { ...acc[siteKey], member_id: member.id };
    writeAccounts(file, acc);
    console.log('saved member_id', member.id, 'for', siteKey);
    break;
  }
  case 'build-content-nodes': {
    // build-content-nodes <structure-json-file> <out-file>
    // Converts a simplified block description into full Ricos nodes, so Claude writes
    // {"type":"heading","level":2,"text":"..."} / {"type":"paragraph","text":"..."} /
    // {"type":"image","url":"...","altText":"..."} instead of hand-rolling Ricos's
    // more verbose nested node/textData/imageData shapes (error-prone by hand).
    const [structureFile, outFile] = args;
    const blocks = readJson(structureFile);
    const nodes = blocks.map((b) => {
      const id = nodeId();
      if (b.type === 'heading') {
        return {
          type: 'HEADING',
          id,
          headingData: { level: b.level || 2, textStyle: {} },
          nodes: [{ type: 'TEXT', textData: { text: b.text, decorations: [] } }],
        };
      }
      if (b.type === 'paragraph') {
        return {
          type: 'PARAGRAPH',
          id,
          paragraphData: { textStyle: {} },
          nodes: [{ type: 'TEXT', textData: { text: b.text, decorations: b.decorations || [] } }],
        };
      }
      if (b.type === 'image') {
        return {
          type: 'IMAGE',
          id,
          imageData: {
            image: { src: { url: b.url } },
            altText: b.altText || '',
            containerData: { width: { size: 'CONTENT' }, alignment: 'CENTER' },
          },
        };
      }
      throw new Error(`build-content-nodes: unknown block type "${b.type}"`);
    });
    fs.writeFileSync(outFile, JSON.stringify(nodes, null, 2));
    console.log('written', outFile, '-', nodes.length, 'nodes');
    break;
  }
  case 'add-link-decoration': {
    // add-link-decoration <content-nodes-json-file> <node-index> <link-text> <url> <out-file>
    // CONFIRMED BUG (live post, 2026-08-01): a "decorations" entry with start/end offsets
    // on a single TEXT node is NOT honored by Wix's Ricos renderer — the LINK decoration
    // was applied to the ENTIRE node's text instead of just the start/end range, turning
    // the whole paragraph into a link. The working approach is to SPLIT the node's text
    // into multiple sibling TEXT children — a plain "before" node, a TEXT node holding only
    // the link phrase with a whole-node LINK decoration (no start/end), and a plain "after"
    // node — mirroring how Ricos actually scopes per-node decorations to a node's full text.
    const [file, nodeIndexArg, linkText, url, outFile] = args;
    const nodes = readJson(file);
    const idx = Number(nodeIndexArg);
    const node = nodes[idx];
    if (!node || !node.nodes || !node.nodes[0] || node.nodes[0].type !== 'TEXT') {
      console.error('add-link-decoration: node', idx, 'has no TEXT child to attach a link to');
      process.exit(1);
    }
    const textNode = node.nodes[0];
    const text = textNode.textData.text;
    const first = text.indexOf(linkText);
    if (first === -1) {
      console.error('add-link-decoration: link text not found in node', idx, '—', JSON.stringify(linkText));
      process.exit(1);
    }
    if (text.indexOf(linkText, first + 1) !== -1) {
      console.error('add-link-decoration: link text appears more than once in node', idx, '— use a longer, unique phrase');
      process.exit(1);
    }
    const before = text.slice(0, first);
    const after = text.slice(first + linkText.length);
    const split = [];
    if (before) split.push({ type: 'TEXT', textData: { text: before, decorations: [] } });
    split.push({
      type: 'TEXT',
      textData: { text: linkText, decorations: [{ type: 'LINK', linkData: { link: { url } } }] },
    });
    if (after) split.push({ type: 'TEXT', textData: { text: after, decorations: [] } });
    node.nodes = split;
    fs.writeFileSync(outFile, JSON.stringify(nodes, null, 2));
    console.log('written', outFile, '- link scoped to', split.length, 'text node(s), link text:', JSON.stringify(linkText));
    break;
  }
  case 'build-post-payload': {
    // build-post-payload <content-nodes-json-file> <title> <member_id> <out-file>
    const [contentFile, title, memberId, outFile] = args;
    const nodes = readJson(contentFile);
    const payload = {
      draftPost: {
        title,
        memberId,
        richContent: { nodes, metadata: { version: 1 } },
      },
      publish: true,
    };
    fs.writeFileSync(outFile, JSON.stringify(payload));
    console.log('written', outFile, fs.statSync(outFile).size, 'bytes', '(nodes:', nodes.length, ')');
    break;
  }
  case 'build-slug-update-payload': {
    // build-slug-update-payload <post-id> <ascii-kebab-slug> <out-file>
    // CreateDraftPost has no seoSlug field — build a payload for a follow-up
    // UpdateDraftPost (PATCH) call to fix the auto-generated Vietnamese-diacritic
    // slug into a clean ASCII one. action:"UPDATE_PUBLICATION" is required because
    // the post is already published (plain "UPDATE" only touches the draft version).
    const [postId, slug, outFile] = args;
    const payload = { draftPost: { id: postId, seoSlug: slug }, action: 'UPDATE_PUBLICATION' };
    fs.writeFileSync(outFile, JSON.stringify(payload));
    console.log('written', outFile, fs.statSync(outFile).size, 'bytes');
    break;
  }
  case 'word-count': {
    // word-count <content-nodes-json-file>
    // Sums words across every TEXT child's textData.text; image nodes are ignored.
    const [file] = args;
    const nodes = readJson(file);
    const words = nodes
      .flatMap((n) => (n.nodes || []).filter((c) => c.type === 'TEXT').map((c) => c.textData.text))
      .join(' ')
      .trim()
      .split(/\s+/)
      .filter(Boolean);
    console.log(words.length);
    break;
  }
  case 'show-import-result': {
    // show-import-result <import-media-response-json-file>
    const [file] = args;
    const r = readJson(file);
    const f = r.file || {};
    console.log(JSON.stringify({ id: f.id, url: f.url, operationStatus: f.operationStatus }, null, 2));
    break;
  }
  case 'show-post-result': {
    // show-post-result <post-response-json-file> <site-domain-or-url>
    // Wix's create-draft-post response does not include a ready-to-browse public URL —
    // it returns internal post metadata. Build a best-effort public URL from the post's
    // "url" field if present (fieldset-dependent), else fall back to the blog's post
    // listing page on the given site domain.
    const [file, siteDomain] = args;
    const r = readJson(file);
    const post = r.draftPost || {};
    const publicUrl = (post.url && post.url.base && post.url.path)
      ? post.url.base + post.url.path
      : (siteDomain ? `https://${siteDomain}/blog` : undefined);
    console.log(JSON.stringify({
      id: post.id,
      title: post.title,
      status: post.status,
      post_url: publicUrl,
    }, null, 2));
    break;
  }
  default:
    console.error('wix-json.js: unknown subcommand', cmd, '(expected: get-account-field|set-credentials|save-member-id|build-content-nodes|add-link-decoration|build-post-payload|build-slug-update-payload|word-count|show-import-result|show-post-result)');
    process.exit(1);
}
