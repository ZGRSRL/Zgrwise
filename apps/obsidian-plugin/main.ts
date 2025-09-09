import { App, Editor, MarkdownView, Plugin, PluginSettingTab, Setting } from 'obsidian';

interface ZgrWiseSettings {
	apiBase: string;
	apiKey: string;
	vaultSubfolder: string;
}

const DEFAULT_SETTINGS: ZgrWiseSettings = {
	apiBase: 'http://localhost:8000',
	apiKey: 'devkey',
	vaultSubfolder: 'ZgrWise'
}

export default class ZgrWisePlugin extends Plugin {
	settings: ZgrWiseSettings;

	async onload() {
		await this.loadSettings();

		// Add command to pull highlights
		this.addCommand({
			id: 'pull-zgrwise-highlights',
			name: 'Pull new highlights from ZgrWise',
			callback: () => this.pullHighlights(),
		});

		// Add settings tab
		this.addSettingTab(new ZgrWiseSettingTab(this.app, this));
	}

	onunload() {

	}

	async loadSettings() {
		this.settings = Object.assign({}, DEFAULT_SETTINGS, await this.loadData());
	}

	async saveSettings() {
		await this.saveData(this.settings);
	}

	async pullHighlights() {
		try {
			const response = await fetch(`${this.settings.apiBase}/api/highlights`, {
				headers: {
					'X-API-Key': this.settings.apiKey
				}
			});

			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}

			const highlights = await response.json();
			
			// Create subfolder if it doesn't exist
			const folderPath = this.settings.vaultSubfolder;
			await this.app.vault.createFolder(folderPath).catch(() => {});

			// Process each highlight
			for (const highlight of highlights) {
				await this.createHighlightFile(highlight, folderPath);
			}

			// Show success message
			new Notice(`Successfully synced ${highlights.length} highlights from ZgrWise`);
		} catch (error) {
			console.error('Error pulling highlights:', error);
			new Notice(`Error syncing highlights: ${error.message}`);
		}
	}

	async createHighlightFile(highlight: any, folderPath: string) {
		const fileName = `${highlight.id}_${highlight.text.substring(0, 50).replace(/[^a-zA-Z0-9]/g, '_')}.md`;
		const filePath = `${folderPath}/${fileName}`;

		// Check if file already exists
		const existingFile = this.app.vault.getAbstractFileByPath(filePath);
		if (existingFile) {
			return; // Skip if already exists
		}

		// Create markdown content
		const content = this.generateMarkdownContent(highlight);

		// Create file
		await this.app.vault.create(filePath, content);
	}

	generateMarkdownContent(highlight: any): string {
		const source = highlight.source;
		
		return `---
title: "${source.title}"
source_url: "${source.url}"
source_type: "${source.type}"
origin: "${source.origin}"
author: "${source.author || 'Unknown'}"
created: "${source.created_at}"
tags: [${source.tags?.join(', ') || ''}]
summary: "${source.summary || ''}"
---

# Highlights

> ${highlight.text}

- note: ${highlight.note || ''}
- added: ${highlight.created_at}
- location: ${highlight.location || ''}

## Source Details

**Title:** ${source.title}
**URL:** ${source.url}
**Type:** ${source.type}
**Origin:** ${source.origin}
**Author:** ${source.author || 'Unknown'}
**Created:** ${source.created_at}

${source.summary ? `**Summary:** ${source.summary}` : ''}

${source.raw ? `**Content:**\n\n${source.raw}` : ''}
`;
	}
}

class ZgrWiseSettingTab extends PluginSettingTab {
	plugin: ZgrWisePlugin;

	constructor(app: App, plugin: ZgrWisePlugin) {
		super(app, plugin);
		this.plugin = plugin;
	}

	display(): void {
		const {containerEl} = this;

		containerEl.empty();

		containerEl.createEl('h2', {text: 'ZgrWise Settings'});

		new Setting(containerEl)
			.setName('API Base URL')
			.setDesc('The base URL of your ZgrWise API')
			.addText(text => text
				.setPlaceholder('http://localhost:8000')
				.setValue(this.plugin.settings.apiBase)
				.onChange(async (value) => {
					this.plugin.settings.apiBase = value;
					await this.plugin.saveSettings();
				}));

		new Setting(containerEl)
			.setName('API Key')
			.setDesc('Your ZgrWise API key')
			.addText(text => text
				.setPlaceholder('devkey')
				.setValue(this.plugin.settings.apiKey)
				.onChange(async (value) => {
					this.plugin.settings.apiKey = value;
					await this.plugin.saveSettings();
				}));

		new Setting(containerEl)
			.setName('Vault Subfolder')
			.setDesc('Subfolder in your vault where highlights will be saved')
			.addText(text => text
				.setPlaceholder('ZgrWise')
				.setValue(this.plugin.settings.vaultSubfolder)
				.onChange(async (value) => {
					this.plugin.settings.vaultSubfolder = value;
					await this.plugin.saveSettings();
				}));
	}
} 