import json
from subprocess import Popen, PIPE

import mysql.connector
import time


def main(urls):
    cnx = mysql.connector.connect(
        user="root",
        password="password",
        host="127.0.0.1",
        database="mysql",
        auth_plugin="mysql_native_password")

    cursor = cnx.cursor()

    for url in urls:
        print(f"__________________________")
        print(f"Collecting stats for {url}")
        p = Popen(
            f"lighthouse {url} --output json --chrome-flags=--headless",
            shell=True,
            stdout=PIPE,
            stderr=PIPE
        )

        stdout, stderr = p.communicate()
        report = json.loads(stdout.decode("UTF-8"))

        categories = report["categories"]
        performance = categories["performance"]["score"]
        accessibility = categories["accessibility"]["score"]
        bestPractices=categories["best-practices"]["score"]
        seo = categories["seo"]["score"]
        pwa = categories["pwa"]["score"]

        audits = report["audits"]
        firstContentfulPaint = audits["first-contentful-paint"]["numericValue"]
        largestContentfulPaint = audits["largest-contentful-paint"]["numericValue"]
        speedIndex = audits["speed-index"]["numericValue"]
        estimatedInputLatency = audits["estimated-input-latency"]["numericValue"]
        firstInputDelay = audits["max-potential-fid"]["numericValue"]
        totalBlockingTime = audits["total-blocking-time"]["numericValue"]
        errorsInConsole = audits["errors-in-console"]["score"]
        serverResponseTime = audits["server-response-time"]["numericValue"]
        interactive = audits["interactive"]["numericValue"]
        cumulativeLayoutShift = audits["cumulative-layout-shift"]["numericValue"]
        

        metrics = report["audits"]["metrics"]["details"]["items"][0]
        observedFirstVisualChange = metrics["observedFirstVisualChange"]
        observedLastVisualChange = metrics["observedLastVisualChange"]

        diagnostics = report["audits"]["diagnostics"]["details"]["items"][0]
        numRequests = diagnostics["numRequests"]
        numScripts = diagnostics["numScripts"]
        numTasksOver10ms = diagnostics["numTasksOver10ms"]
        numTasksOver25ms = diagnostics["numTasksOver25ms"]
        numTasksOver50ms = diagnostics["numTasksOver50ms"]
        numTasksOver100ms = diagnostics["numTasksOver100ms"]
        numTasksOver500ms = diagnostics["numTasksOver500ms"]
        maxRtt = diagnostics["maxRtt"]
        maxServerLatency = diagnostics["maxServerLatency"]
        mainDocumentTransferSize = diagnostics["mainDocumentTransferSize"]
        totalByteWeight = diagnostics["totalByteWeight"]
        totalTaskTime = diagnostics["totalTaskTime"]

        site = url.split("://")[-1]

        print(f"Site: {site}")
        print(f"performance: {performance}")
        print(f"accessibility: {accessibility}")
        print(f"bestPractices: {bestPractices}")
        print(f"seo: {seo}")
        print(f"pwa: {pwa}")
        print(f"firstContentfulPaint: {firstContentfulPaint}")
        print(f"largestContentfulPaint: {largestContentfulPaint}")
        print(f"speedIndex: {speedIndex}")
        print(f"estimatedInputLatency: {estimatedInputLatency}")
        print(f"totalBlockingTime: {totalBlockingTime}")
        print(f"errorsInConsole: {errorsInConsole}")
        print(f"serverResponseTime: {serverResponseTime}")
        print(f"interactive: {interactive}")
        print(f"observedFirstVisualChange: {observedFirstVisualChange}")
        print(f"observedLastVisualChange: {observedLastVisualChange}")
        print(f"numRequests: {numRequests}")
        print(f"numScripts: {numScripts}")
        print(f"cumulativeLayoutShift: {cumulativeLayoutShift}")
        print(f"firstInputDelay: {firstInputDelay}")
        print(f"numTasksOver10ms: {numTasksOver10ms}")
        print(f"numTasksOver25ms: {numTasksOver25ms}")
        print(f"numTasksOver50ms: {numTasksOver50ms}")
        print(f"numTasksOver100ms: {numTasksOver100ms}")
        print(f"numTasksOver500ms: {numTasksOver500ms}")
        print(f"maxRtt: {maxRtt}")
        print(f"maxServerLatency: {maxServerLatency}")
        print(f"mainDocumentTransferSize: {mainDocumentTransferSize}")
        print(f"totalByteWeight: {totalByteWeight}")
        print(f"totalTaskTime: {totalTaskTime}")
        

        metrics={
            "performance": performance,
            "accessibility": accessibility,
            "bestPractices": bestPractices,
            "seo":seo,
            "pwa":pwa,
            "firstContentfulPaint":firstContentfulPaint,
            "firstInputDelay":firstInputDelay,
            "largestContentfulPaint":largestContentfulPaint,
            "speedIndex":speedIndex,
            "estimatedInputLatency":estimatedInputLatency,
            "totalBlockingTime":totalBlockingTime,
            "errorsInConsole":errorsInConsole,
            "serverResponseTime":serverResponseTime,
            "interactive":interactive,
            "observedFirstVisualChange":observedFirstVisualChange,
            "observedLastVisualChange":observedLastVisualChange,
            "cumulativeLayoutShift":cumulativeLayoutShift,
            "numRequests":numRequests,
            "numScripts":numScripts,
            "numTasksOver10ms":numTasksOver10ms,
            "numTasksOver25ms":numTasksOver25ms,
            "numTasksOver50ms":numTasksOver50ms,
            "numTasksOver100ms":numTasksOver100ms,
            "numTasksOver500ms":numTasksOver500ms,
            "maxRtt":maxRtt,
            "maxServerLatency":maxServerLatency,
            "mainDocumentTransferSize":mainDocumentTransferSize,
            "totalByteWeight":totalByteWeight,
            "totalTaskTime":totalTaskTime
        }

        for name, value in metrics.items():
            cursor.execute(
                f"INSERT INTO mysql.lh_reports_1 (site, metric_name, metric_value)"
                f"VALUES ('{site}', '{name}', {value})"
            )
        cursor.execute("COMMIT")

    cursor.close()
    cnx.close()


if __name__ == "__main__":
    main(["https://cowab.se", "https://cowab.no"])
    