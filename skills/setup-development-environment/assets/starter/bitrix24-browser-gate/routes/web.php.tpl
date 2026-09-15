<?php

use App\Http\Controllers\Bitrix24AppController;
use Illuminate\Support\Facades\Route;

Route::get('/', [Bitrix24AppController::class, 'index'])->name('bitrix24.app');
Route::match(['get', 'post'], '/bitrix24/launch', [Bitrix24AppController::class, 'launch'])
    ->middleware('throttle:20,1')
    ->name('bitrix24.launch');

Route::get('/health', static fn () => response()->json(['status' => 'ok']))->name('health');
