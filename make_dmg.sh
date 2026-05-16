#!/bin/bash
# ─────────────────────────────────────────────────────
#  Create DMG installer for Hermes Translate
#  Usage: ./make_dmg.sh
# ─────────────────────────────────────────────────────
set -e

APP_NAME="Hermes Translate"
APP_PATH="dist/${APP_NAME}.app"
DMG_NAME="Hermes-Translate-0.0.2.dmg"
DMG_PATH="dist/${DMG_NAME}"
STAGING="/tmp/hermes-dmg-staging"

if [ ! -d "$APP_PATH" ]; then
    echo "❌ $APP_PATH not found. Run py2app first."
    exit 1
fi

echo "📦 Creating DMG installer..."

# Clean up
rm -rf "$STAGING" "$DMG_PATH"
mkdir -p "$STAGING"

# Copy app
cp -R "$APP_PATH" "$STAGING/"

# Create Applications symlink (for drag-to-install)
ln -s /Applications "$STAGING/Applications"

# Create DMG
hdiutil create \
    -volname "$APP_NAME" \
    -srcfolder "$STAGING" \
    -ov \
    -format UDZO \
    -imagekey zlib-level=9 \
    "$DMG_PATH" \
    2>&1 | grep -v "^$"

# Clean up
rm -rf "$STAGING"

# Show result
echo ""
echo "✅ DMG created: $DMG_PATH"
echo "   Size: $(du -sh "$DMG_PATH" | cut -f1)"
echo ""
echo "📌 To install:"
echo "   1. Double-click $DMG_NAME"
echo "   2. Drag 'Hermes Translate' to Applications"
echo "   3. Launch from Applications or Spotlight"
