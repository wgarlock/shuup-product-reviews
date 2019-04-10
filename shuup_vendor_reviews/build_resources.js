/**
 * This file is part of Shuup Product Reviews.
 *
 * Copyright (c) 2012-2019, Shoop Commerce Ltd. All rights reserved.
 *
 * This source code is licensed under the OSL-3.0 license found in the
 * LICENSE file in the root directory of this source tree.
 */
const { getParcelBuildCommand, runBuildCommands } = require("shuup-static-build-tools");

runBuildCommands([
    getParcelBuildCommand({
        cacheDir: "shuup-vendor-reviews",
        outputDir: "static/shuup_vendor_reviews",
        outputFileName: "shuup_vendor_reviews",
        entryFile: "../shuup_product_reviews/static_src/index.js"
    })
]);
