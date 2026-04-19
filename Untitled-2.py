import React, { useState, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import { AlertCircle, Play, FileDown, LayoutGrid, Table2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

import SettingsSidebar from '@/components/optimizer/SettingsSidebar';
import PiecesTable from '@/components/optimizer/PiecesTable';
import BoardCanvas from '@/components/optimizer/BoardCanvas';
import ResultsSummary from '@/components/optimizer/ResultsSummary';
import { optimizeCutting } from '@/lib/optimizer';
import { exportToPDF } from '@/lib/pdfExporter';

const DEFAULT_SETTINGS = {
  kerf: 3.2,
  trim: 10,
  boardLength: 2800,
  boardWidth: 2070,
  boardThick: 18,
};

const SAMPLE_PIECES = [
  { id: 1, name: 'جانب خزانة', finalLength: 720, finalWidth: 400, quantity: 2, grain: 'L', edgeLeft: 0.5, edgeRight: 0.5, edgeTop: 0.5, edgeBottom: 0 },
  { id: 2, name: 'رف علوي',    finalLength: 800, finalWidth: 380, quantity: 1, grain: 'any', edgeLeft: 0.5, edgeRight: 0.5, edgeTop: 0, edgeBottom: 0 },
  { id: 3, name: 'قاعدة',      finalLength: 800, finalWidth: 400, quantity: 1, grain: 'any', edgeLeft: 0.5, edgeRight: 0.5, edgeTop: 0.5, edgeBottom: 0.5 },
  { id: 4, name: 'باب',        finalLength: 700, finalWidth: 390, quantity: 2, grain: 'L', edgeLeft: 1, edgeRight: 1, edgeTop: 1, edgeBottom: 1 },
  { id: 5, name: 'رف وسطي',    finalLength: 798, finalWidth: 378, quantity: 3, grain: 'any', edgeLeft: 0, edgeRight: 0, edgeTop: 0, edgeBottom: 0 },
];

export default function Optimizer() {
  const [settings, setSettings]   = useState(DEFAULT_SETTINGS);
  const [pieces, setPieces]       = useState(SAMPLE_PIECES);
  const [boards, setBoards]       = useState([]);
  const [errors, setErrors]       = useState([]);
  const [running, setRunning]     = useState(false);
  const [activeTab, setActiveTab] = useState('pieces');

  const handleSettingChange = useCallback((key, val) => {
    setSettings(s => ({ ...s, [key]: val }));
  }, []);

  const boardArea = (settings.boardLength - 2 * settings.trim) * (settings.boardWidth - 2 * settings.trim);

  const runOptimizer = () => {
    setRunning(true);
    setErrors([]);
    setTimeout(() => {
      try {
        const result = optimizeCutting(
          pieces,
          settings.boardLength,
          settings.boardWidth,
          settings.trim,
          settings.kerf
        );
        setBoards(result);
        setActiveTab('layout');
      } catch (e) {
        setErrors([e.message]);
      }
      setRunning(false);
    }, 50);
  };

  const handleExportPDF = () => {
    exportToPDF({ boards, settings, pieces, boardArea });
  };

  const canvasScale = Math.min(
    600 / (settings.boardWidth  - 2 * settings.trim),
    400 / (settings.boardLength - 2 * settings.trim),
    0.35
  );

  return (
    <div className="flex min-h-screen bg-background font-cairo" dir="rtl">
      {/* Sidebar */}
      <SettingsSidebar settings={settings} onChange={handleSettingChange} />

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* Top Bar */}
        <header className="flex items-center justify-between px-6 py-3 border-b border-border bg-card shadow-sm">
          <div>
            <h2 className="font-bold text-base text-foreground">محسّن تقطيع الألواح الخشبية</h2>
            <p className="text-xs text-muted-foreground mt-0.5">
              {pieces.length} قطعة · لوح {settings.boardLength}×{settings.boardWidth}×{settings.boardThick}mm
            </p>
          </div>
          <div className="flex gap-2">
            {boards.length > 0 && (
              <Button variant="outline" size="sm" onClick={handleExportPDF} className="gap-1.5 text-xs h-8">
                <FileDown className="w-3.5 h-3.5" />
                تصدير PDF
              </Button>
            )}
            <Button
              size="sm" onClick={runOptimizer}
              disabled={running || pieces.length === 0}
              className="gap-1.5 text-xs h-8 bg-primary hover:bg-primary/90"
            >
              <Play className="w-3.5 h-3.5" />
              {running ? 'جاري التحسين...' : 'تشغيل المحسّن'}
            </Button>
          </div>
        </header>

        {/* Errors */}
        <AnimatePresence>
          {errors.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
              className="mx-6 mt-3 p-3 bg-destructive/10 border border-destructive/30 rounded-lg flex gap-2 items-start text-sm text-destructive"
            >
              <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
              <div>{errors.map((e, i) => <p key={i}>{e}</p>)}</div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Tabs */}
        <div className="flex-1 overflow-hidden flex flex-col p-4 gap-4">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col">
            <TabsList className="w-fit bg-muted rounded-lg h-9 self-start">
              <TabsTrigger value="pieces" className="text-xs gap-1.5 h-7 px-3">
                <Table2 className="w-3.5 h-3.5" />
                القطع
              </TabsTrigger>
              <TabsTrigger value="layout" className="text-xs gap-1.5 h-7 px-3" disabled={boards.length === 0}>
                <LayoutGrid className="w-3.5 h-3.5" />
                التخطيط {boards.length > 0 && `(${boards.length} لوح)`}
              </TabsTrigger>
            </TabsList>

            {/* Pieces Tab */}
            <TabsContent value="pieces" className="flex-1 mt-4 overflow-auto">
              <PiecesTable pieces={pieces} onChange={setPieces} />
              {pieces.length > 0 && (
                <div className="mt-4 p-3 bg-muted/40 rounded-lg border border-border text-xs text-muted-foreground">
                  <span className="font-bold text-foreground">ملاحظة: </span>
                  "قطع ف." = الطول النهائي ناقص شريط الحافة. "قطع ع." = العرض النهائي ناقص شريط الحافة. هذه هي الأبعاد الفعلية التي ستُقطع.
                </div>
              )}
            </TabsContent>

            {/* Layout Tab */}
            <TabsContent value="layout" className="flex-1 mt-4 overflow-auto">
              {boards.length > 0 && (
                <div className="flex flex-col gap-6">
                  <ResultsSummary boards={boards} boardArea={boardArea} />

                  <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
                    {boards.map((board, bi) => (
                      <motion.div
                        key={board.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: bi * 0.1 }}
                        className="bg-card border border-border rounded-xl p-4 shadow-sm"
                      >
                        <BoardCanvas
                          board={board}
                          boardIndex={bi}
                          scale={canvasScale}
                        />

                        {/* جدول قطع اللوح */}
                        <div className="mt-3 overflow-x-auto">
                          <table className="w-full text-xs">
                            <thead>
                              <tr className="border-b border-border text-muted-foreground">
                                <th className="text-right py-1 px-2 font-semibold">القطعة</th>
                                <th className="text-center py-1 px-2 font-semibold">الموضع X</th>
                                <th className="text-center py-1 px-2 font-semibold">الموضع Y</th>
                                <th className="text-center py-1 px-2 font-semibold">العرض</th>
                                <th className="text-center py-1 px-2 font-semibold">الطول</th>
                                <th className="text-center py-1 px-2 font-semibold">مدور</th>
                              </tr>
                            </thead>
                            <tbody>
                              {board.placedPieces.map((p, i) => (
                                <tr key={i} className={i % 2 === 0 ? 'bg-muted/10' : ''}>
                                  <td className="py-1 px-2 font-medium">{p.label || p.name}</td>
                                  <td className="py-1 px-2 text-center">{p.x.toFixed(0)}</td>
                                  <td className="py-1 px-2 text-center">{p.y.toFixed(0)}</td>
                                  <td className="py-1 px-2 text-center">{p.w.toFixed(0)}</td>
                                  <td className="py-1 px-2 text-center">{p.h.toFixed(0)}</td>
                                  <td className="py-1 px-2 text-center">{p.rotated ? '✓' : '—'}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                </div>
              )}
            </TabsContent>
          </Tabs>
        </div>
      </main>
    </div>
  );
}