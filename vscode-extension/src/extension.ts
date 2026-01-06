import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';
import { execFile } from 'child_process';
import { promisify } from 'util';

const execFileAsync = promisify(execFile);

interface FixupConfig {
  enable: boolean;
  fixupOnSave: boolean;
  path: string;
  width: number;
  skipRules: string[];
}

function getConfig(): FixupConfig {
  const config = vscode.workspace.getConfiguration('md-fixup');
  return {
    enable: config.get<boolean>('enable', true),
    fixupOnSave: config.get<boolean>('fixupOnSave', false),
    path: config.get<string>('path', ''),
    width: config.get<number>('width', 60),
    skipRules: config.get<string[]>('skipRules', []),
  };
}

async function findMdFixupExecutable(): Promise<string | null> {
  const config = getConfig();

  // If path is explicitly set, use it
  if (config.path) {
    if (fs.existsSync(config.path)) {
      return config.path;
    }
    // Try with executable name appended
    const withExe = path.join(config.path, process.platform === 'win32' ? 'md-fixup.exe' : 'md-fixup');
    if (fs.existsSync(withExe)) {
      return withExe;
    }
  }

  // Try common locations
  const possiblePaths = [
    'md-fixup', // System PATH
    path.join(os.homedir(), '.cargo', 'bin', 'md-fixup'),
    path.join(os.homedir(), '.local', 'bin', 'md-fixup'),
    '/usr/local/bin/md-fixup',
    '/opt/homebrew/bin/md-fixup', // macOS Homebrew
  ];

  // On Windows, also try with .exe extension
  if (process.platform === 'win32') {
    possiblePaths.push('md-fixup.exe');
  }

  for (const exePath of possiblePaths) {
    try {
      // Try to execute with --help to verify it's the right binary
      await execFileAsync(exePath, ['--help'], { timeout: 2000 });
      return exePath;
    } catch (error) {
      // Continue searching
    }
  }

  return null;
}

async function formatDocument(document: vscode.TextDocument): Promise<string | null> {
  const config = getConfig();

  if (!config.enable) {
    return null;
  }

  const executable = await findMdFixupExecutable();
  if (!executable) {
    vscode.window.showErrorMessage(
      'md-fixup executable not found. Please install md-fixup or set the "md-fixup.path" setting.'
    );
    return null;
  }

  // Create a temporary file with the document content
  const tempFile = path.join(os.tmpdir(), `md-fixup-${Date.now()}.md`);

  try {
    // Write document content to temp file
    fs.writeFileSync(tempFile, document.getText(), 'utf8');

    // Build command arguments
    const args: string[] = ['--overwrite'];

    if (config.width > 0) {
      args.push('--width', config.width.toString());
    }

    if (config.skipRules.length > 0) {
      args.push('--skip', config.skipRules.join(','));
    }

    args.push(tempFile);

    // Execute md-fixup
    try {
      await execFileAsync(executable, args, { timeout: 30000 });

      // Read the formatted content
      const formattedContent = fs.readFileSync(tempFile, 'utf8');
      return formattedContent;
    } catch (error: any) {
      const errorMessage = error.stderr || error.message || 'Unknown error';
      vscode.window.showErrorMessage(`md-fixup error: ${errorMessage}`);
      return null;
    }
  } finally {
    // Clean up temp file
    try {
      if (fs.existsSync(tempFile)) {
        fs.unlinkSync(tempFile);
      }
    } catch (error) {
      // Ignore cleanup errors
    }
  }
}

async function formatDocumentCommand(textEditor: vscode.TextEditor, edit: vscode.TextEditorEdit) {
  const document = textEditor.document;

  if (document.languageId !== 'markdown') {
    vscode.window.showWarningMessage('Markdown Fixup can only format Markdown files.');
    return;
  }

  const formatted = await formatDocument(document);
  if (formatted === null) {
    return;
  }

  // Replace entire document content
  const fullRange = new vscode.Range(
    document.positionAt(0),
    document.positionAt(document.getText().length)
  );

  edit.replace(fullRange, formatted);
}

export function activate(context: vscode.ExtensionContext) {
  // Register format document command
  const formatCommand = vscode.commands.registerTextEditorCommand(
    'md-fixup.formatDocument',
    formatDocumentCommand
  );
  context.subscriptions.push(formatCommand);

  // Register format on save
  const onSaveDisposable = vscode.workspace.onDidSaveTextDocument(async (document) => {
    const config = getConfig();

    if (!config.fixupOnSave || !config.enable) {
      return;
    }

    if (document.languageId !== 'markdown') {
      return;
    }

    // Format the document after save
    const formatted = await formatDocument(document);
    if (formatted === null) {
      return;
    }

    // Apply edits
    const edit = new vscode.WorkspaceEdit();
    const fullRange = new vscode.Range(
      document.positionAt(0),
      document.positionAt(document.getText().length)
    );
    edit.replace(document.uri, fullRange, formatted);

    const success = await vscode.workspace.applyEdit(edit);
    if (success) {
      // Save the document again to persist the changes
      await document.save();
    }
  });
  context.subscriptions.push(onSaveDisposable);

  // Register as document formatter
  const formatter = vscode.languages.registerDocumentFormattingEditProvider('markdown', {
    async provideDocumentFormattingEdits(
      document: vscode.TextDocument,
      options: vscode.FormattingOptions,
      token: vscode.CancellationToken
    ): Promise<vscode.TextEdit[]> {
      const config = getConfig();

      if (!config.enable) {
        return [];
      }

      const formatted = await formatDocument(document);
      if (formatted === null) {
        return [];
      }

      const fullRange = new vscode.Range(
        document.positionAt(0),
        document.positionAt(document.getText().length)
      );

      return [vscode.TextEdit.replace(fullRange, formatted)];
    }
  });
  context.subscriptions.push(formatter);
}

export function deactivate() {}
