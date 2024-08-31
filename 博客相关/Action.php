<?php

class Export2Hugo_Action extends Typecho_Widget implements Widget_Interface_Do
{
    /**
     * 导出文章
     *
     * @access public
     * @return void
     */
    public function doExport()
    {
        try {
            $db = Typecho_Db::get();
            $prefix = $db->getPrefix();

            $sql = <<<SQL
            SELECT 
                u.screenName AS author,
                u.url AS authorUrl,
                c.title,
                c.type,
                c.text,
                c.created,
                c.status,
                c.password,
                t2.category,
                t1.tags,
                c.slug 
            FROM {$prefix}contents c
            LEFT JOIN (
                SELECT cid, GROUP_CONCAT(m.name, '","') AS tags 
                FROM {$prefix}metas m
                JOIN {$prefix}relationships r ON m.mid = r.mid 
                WHERE m.type = 'tag' 
                GROUP BY cid
            ) t1 ON c.cid = t1.cid
            LEFT JOIN (
                SELECT cid, GROUP_CONCAT(m.name, '","') AS category 
                FROM {$prefix}metas m
                JOIN {$prefix}relationships r ON m.mid = r.mid 
                WHERE m.type = 'category' 
                GROUP BY cid
            ) t2 ON c.cid = t2.cid
            LEFT JOIN {$prefix}users u ON c.authorId = u.uid
            WHERE c.type IN ('post', 'page')
SQL;

            $result = $db->query($sql);
            if ($result === false) {
                throw new Exception("Database query failed: " . $db->getLastError());
            }
            $contents = $db->fetchAll($result);

            $tempDir = sys_get_temp_dir() . "/Export2Hugo_" . uniqid();
            if (file_exists($tempDir)) {
                $this->rrmdir($tempDir);
            }
            mkdir($tempDir);

            $contentDir = $tempDir . "/content/";
            mkdir($contentDir);
            mkdir($contentDir . "posts");

            foreach ($contents as $content) {
                $title = $this->sanitizeString($content["title"]);
                $categories = $content["category"] ? '"' . trim($content["category"], ',"') . '"' : '';
                $tags = $content["tags"] ? '"' . trim($content["tags"], ',"') . '"' : '';
                $slug = $content["slug"];
                $time = date('Y-m-d H:i:s', $content["created"]);
                $text = str_replace("<!--markdown-->", "", $content["text"]);
                $draft = $content["status"] !== "publish" || $content["password"] ? "true" : "false";
                $hugo = <<<TMP
---
title: "$title"
date: "$time"
draft: $draft
aliases: []
cascade: {}
description: ""
expiryDate: ""
headless: false
isCJKLanguage: false
keywords: []
lastmod: ""
layout: ""
linkTitle: ""
markup: ""
outputs: []
params:
  author: "{$content['author']}"
publishDate: ""
resources: []
sitemap: {}
slug: "$slug"
summary: ""
translationKey: ""
type: "{$content['type']}"
url: ""
weight: 0
categories: [ $categories ]
tags: [ $tags ]
---

$text
TMP;

                $filename = $this->sanitizeString($title) . ".md";

                if ($content["type"] === "post") {
                    $filename = "posts/" . $filename;
                }
                file_put_contents($contentDir . $filename, $hugo);
            }

            $outputFilename = "hugo." . date('Y-m-d') . ".tar.gz";
            $tempOutputFile = tempnam(sys_get_temp_dir(), 'hugo_export_');

            // 使用 PharData 创建 tar.gz 文件
            $phar = new PharData($tempOutputFile . '.tar');
            $phar->buildFromDirectory($contentDir);
            $phar->compress(Phar::GZ);

            // 重命名压缩后的文件
            $finalOutputFile = $tempOutputFile . '.tar.gz';
            rename($tempOutputFile . '.tar.gz', $finalOutputFile);

            // 设置适当的头部
            header("Content-Type: application/gzip");
            header("Content-Disposition: attachment; filename=$outputFilename");
            header("Content-Length: " . filesize($finalOutputFile));
            header("Pragma: no-cache");
            header("Expires: 0");

            // 输出文件内容
            readfile($finalOutputFile);

            // 清理临时文件和目录
            unlink($finalOutputFile);
            unlink($tempOutputFile);
            $this->rrmdir($tempDir);

        } catch (Exception $e) {
            header('HTTP/1.1 500 Internal Server Error');
            echo "An error occurred: " . $e->getMessage();
            error_log("Export2Hugo Error: " . $e->getMessage() . "\n" . $e->getTraceAsString());

            if ($e instanceof Typecho_Db_Exception) {
                echo "\nDatabase Error: " . $e->getCode() . " " . $e->getMessage();
                error_log("Database Error: " . $e->getCode() . " " . $e->getMessage());
            }
        }
    }

    /**
     * 绑定动作
     *
     * @access public
     * @return void
     */
    public function action()
    {
        $this->widget('Widget_User')->pass('administrator');
        $this->on($this->request->is('export'))->doExport();
    }

    /**
     * 递归删除目录
     *
     * @param string $dir
     * @return bool
     */
    private function rrmdir($dir)
    {
        if (is_dir($dir)) {
            $objects = scandir($dir);
            foreach ($objects as $object) {
                if ($object != "." && $object != "..") {
                    if (is_dir($dir . "/" . $object)) {
                        $this->rrmdir($dir . "/" . $object);
                    } else {
                        unlink($dir . "/" . $object);
                    }
                }
            }
            rmdir($dir);
        }
    }

    /**
     * 清理字符串，用于文件名
     *
     * @param string $string
     * @return string
     */
    private function sanitizeString($string)
    {
        $string = preg_replace('/[^\p{L}\p{N}\s-]/u', '', $string);
        $string = preg_replace('/[\s-]+/', '-', $string);
        $string = trim($string, '-');
        return $string;
    }
}
