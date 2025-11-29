#!/usr/bin/env node

/**
 * Script de Migration Automatique du Système de Thème CHNeoWave
 * 
 * Ce script identifie et corrige automatiquement les composants
 * qui n'utilisent pas le système de thème global.
 */

const fs = require('fs');
const path = require('path');

// Fichiers à migrer
const filesToMigrate = [
  'src/components/Header.tsx',
  'src/components/Sidebar.tsx',
  'src/components/WaveMetricsPanel.tsx',
  'src/pages/DashboardPage.tsx',
  'src/pages/AcquisitionPage.tsx',
  'src/pages/CalibrationPage.tsx',
  'src/pages/AnalysisPage.tsx',
  'src/pages/ExportPage.tsx',
  'src/pages/ProjectPage.tsx',
  'src/ModernAcquisitionPage.tsx',
  'src/ScientificChartContainer.tsx',
  'src/AcquisitionControls.tsx',
  'src/InnovativeSidebar.tsx'
];

// Patterns à rechercher et remplacer
const patterns = [
  {
    name: 'Import useTheme',
    search: /import React.*from 'react';/,
    replace: "import React from 'react';\nimport { useTheme } from '../contexts/ThemeContext';"
  },
  {
    name: 'Ajouter useTheme hook',
    search: /const \w+:\s*React\.FC.*=.*\(\s*\)\s*=>\s*{/,
    replace: (match) => {
      return match.replace('() => {', '() => {\n  const { currentTheme } = useTheme();');
    }
  },
  {
    name: 'Remplacer bg-slate-800',
    search: /bg-slate-800/,
    replace: 'style={{backgroundColor: "var(--bg-elevated)"}}'
  },
  {
    name: 'Remplacer text-white',
    search: /text-white/,
    replace: 'style={{color: "var(--text-primary)"}}'
  }
];

function migrateFile(filePath) {
  try {
    const fullPath = path.join(process.cwd(), filePath);
    
    if (!fs.existsSync(fullPath)) {
      console.log(`⚠️  Fichier non trouvé: ${filePath}`);
      return false;
    }

    let content = fs.readFileSync(fullPath, 'utf8');
    let modified = false;

    // Vérifier si le fichier utilise déjà useTheme
    if (content.includes('useTheme')) {
      console.log(`✅ ${filePath} - Déjà migré`);
      return true;
    }

    // Appliquer les patterns
    patterns.forEach(pattern => {
      if (pattern.search.test(content)) {
        content = content.replace(pattern.search, pattern.replace);
        modified = true;
        console.log(`🔧 ${filePath} - ${pattern.name}`);
      }
    });

    if (modified) {
      fs.writeFileSync(fullPath, content, 'utf8');
      console.log(`✅ ${filePath} - Migré avec succès`);
      return true;
    } else {
      console.log(`ℹ️  ${filePath} - Aucune modification nécessaire`);
      return false;
    }

  } catch (error) {
    console.error(`❌ Erreur lors de la migration de ${filePath}:`, error.message);
    return false;
  }
}

function main() {
  console.log('🚀 Début de la migration automatique du système de thème...\n');

  let migratedCount = 0;
  let totalCount = filesToMigrate.length;

  filesToMigrate.forEach(file => {
    if (migrateFile(file)) {
      migratedCount++;
    }
  });

  console.log(`\n📊 Résumé de la migration:`);
  console.log(`   - Fichiers traités: ${totalCount}`);
  console.log(`   - Fichiers migrés: ${migratedCount}`);
  console.log(`   - Fichiers inchangés: ${totalCount - migratedCount}`);

  if (migratedCount > 0) {
    console.log('\n✅ Migration terminée avec succès!');
    console.log('🔍 Vérifiez les fichiers migrés et testez l\'application.');
  } else {
    console.log('\nℹ️  Aucune migration nécessaire - tous les fichiers sont déjà à jour.');
  }
}

// Exécuter le script
if (require.main === module) {
  main();
}

module.exports = { migrateFile, patterns };
